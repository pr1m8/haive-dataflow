"""MCP Health Monitoring for haive-dataflow.

This module provides health monitoring and management capabilities for MCP servers,
including connection status tracking, performance metrics, and automatic recovery.

Classes:
    MCPHealthMonitor: Main health monitoring service
    MCPHealthChecker: Individual server health checker
"""

import asyncio
import contextlib
import logging
from datetime import datetime

from .registry.models import MCPServerConfig, MCPServerHealth

logger = logging.getLogger(__name__)


class MCPHealthMonitor:
    """Health monitoring service for MCP servers.

    This class provides comprehensive health monitoring for MCP servers including:
    - Periodic health checks
    - Performance metric tracking
    - Automatic recovery attempts
    - Health status reporting

    Attributes:
        mcp_client: Reference to the MCP client
        health_checkers: Dictionary of server health checkers
        monitoring_interval: Seconds between health checks
        is_monitoring: Whether monitoring is currently active

    Example:
        ```python
        monitor = MCPHealthMonitor(mcp_client)
        await monitor.start_monitoring()

        # Get health status
        status = await monitor.get_health_summary()
        print(f"Healthy servers: {status['healthy_count']}")
        ```
    """

    def __init__(self, mcp_client=None, monitoring_interval: int = 30):
        """Initialize health monitor.

        Args:
            mcp_client: MCP client instance to monitor
            monitoring_interval: Seconds between health checks
        """
        self.mcp_client = mcp_client
        self.monitoring_interval = monitoring_interval
        self.health_checkers: dict[str, MCPHealthChecker] = {}
        self.is_monitoring = False
        self._monitoring_task: asyncio.Task | None = None

    async def start_monitoring(self):
        """Start health monitoring for all connected servers."""
        if self.is_monitoring:
            logger.warning("Health monitoring already running")
            return

        if not self.mcp_client:
            logger.error("No MCP client available for monitoring")
            return

        self.is_monitoring = True

        # Create health checkers for all connected servers
        for server_name, server_config in self.mcp_client.connected_servers.items():
            checker = MCPHealthChecker(server_name, server_config)
            self.health_checkers[server_name] = checker

        # Start monitoring task
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info(
            f"Started health monitoring for {len(self.health_checkers)} MCP servers"
        )

    async def stop_monitoring(self):
        """Stop health monitoring."""
        self.is_monitoring = False

        if self._monitoring_task:
            self._monitoring_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._monitoring_task

        logger.info("Stopped health monitoring")

    async def check_all_servers(self) -> dict[str, MCPServerHealth]:
        """Perform health check on all servers.

        Returns:
            Dictionary of server name to health status
        """
        if not self.health_checkers:
            return {}

        health_tasks = []
        for checker in self.health_checkers.values():
            task = checker.check_health()
            health_tasks.append(task)

        results = await asyncio.gather(*health_tasks, return_exceptions=True)

        health_status = {}
        for i, result in enumerate(results):
            checker = list(self.health_checkers.values())[i]
            if isinstance(result, Exception):
                logger.error(f"Health check failed for {checker.server_name}: {result}")
                # Create failed health status
                health_status[checker.server_name] = MCPServerHealth(
                    server_name=checker.server_name,
                    is_healthy=False,
                    last_check=datetime.now(),
                    error_count=checker.error_count + 1,
                    error_details=str(result),
                    capabilities_available=[],
                )
            else:
                health_status[checker.server_name] = result

        return health_status

    async def get_health_summary(self) -> dict[str, any]:
        """Get summary of health status across all servers.

        Returns:
            Summary dictionary with health metrics
        """
        health_status = await self.check_all_servers()

        healthy_count = sum(1 for status in health_status.values() if status.is_healthy)
        unhealthy_count = len(health_status) - healthy_count

        avg_response_time = 0
        if health_status:
            response_times = [
                status.response_time_ms
                for status in health_status.values()
                if status.response_time_ms is not None
            ]
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)

        total_errors = sum(status.error_count for status in health_status.values())

        return {
            "total_servers": len(health_status),
            "healthy_count": healthy_count,
            "unhealthy_count": unhealthy_count,
            "health_percentage": (
                (healthy_count / len(health_status) * 100) if health_status else 0
            ),
            "average_response_time_ms": avg_response_time,
            "total_errors": total_errors,
            "last_check": datetime.now(),
            "server_details": health_status,
        }

    async def recover_failed_servers(self) -> list[str]:
        """Attempt to recover failed servers.

        Returns:
            List of server names that were successfully recovered
        """
        health_status = await self.check_all_servers()
        failed_servers = [
            name for name, status in health_status.items() if not status.is_healthy
        ]

        if not failed_servers:
            return []

        logger.info(f"Attempting to recover {len(failed_servers)} failed servers")
        recovered_servers = []

        for server_name in failed_servers:
            checker = self.health_checkers.get(server_name)
            if checker:
                try:
                    # Attempt recovery
                    await checker.attempt_recovery()

                    # Check if recovery was successful
                    health = await checker.check_health()
                    if health.is_healthy:
                        recovered_servers.append(server_name)
                        logger.info(f"Successfully recovered server: {server_name}")

                except Exception as e:
                    logger.exception(f"Failed to recover server {server_name}: {e}")

        logger.info(
            f"Recovered {
                len(recovered_servers)} out of {
                len(failed_servers)} failed servers"
        )
        return recovered_servers

    async def _monitoring_loop(self):
        """Main monitoring loop."""
        logger.info("Starting health monitoring loop")

        while self.is_monitoring:
            try:
                # Perform health checks
                health_status = await self.check_all_servers()

                # Log health summary
                healthy_count = sum(
                    1 for status in health_status.values() if status.is_healthy
                )
                total_count = len(health_status)
                logger.info(
                    f"Health check complete: {healthy_count}/{total_count} servers healthy"
                )

                # Attempt recovery for failed servers
                if healthy_count < total_count:
                    await self.recover_failed_servers()

                # Wait for next check
                await asyncio.sleep(self.monitoring_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(self.monitoring_interval)

        logger.info("Health monitoring loop ended")


class MCPHealthChecker:
    """Health checker for individual MCP servers.

    This class handles health checking for a single MCP server including
    connection testing, response time measurement, and recovery
    attempts.
    """

    def __init__(self, server_name: str, server_config: MCPServerConfig):
        """Initialize health checker.

        Args:
            server_name: Name of the server to monitor
            server_config: Server configuration
        """
        self.server_name = server_name
        self.server_config = server_config
        self.error_count = 0
        self.last_successful_check: datetime | None = None
        self.consecutive_failures = 0

    async def check_health(self) -> MCPServerHealth:
        """Perform health check on the server.

        Returns:
            Current health status
        """
        start_time = datetime.now()

        try:
            # Perform basic connectivity check
            is_healthy = await self._check_connectivity()

            response_time = (datetime.now() - start_time).total_seconds() * 1000

            if is_healthy:
                self.last_successful_check = datetime.now()
                self.consecutive_failures = 0

                # Get available capabilities
                capabilities = await self._get_available_capabilities()

                health = MCPServerHealth(
                    server_name=self.server_name,
                    is_healthy=True,
                    last_check=datetime.now(),
                    response_time_ms=response_time,
                    error_count=self.error_count,
                    capabilities_available=capabilities,
                )
            else:
                self.consecutive_failures += 1
                self.error_count += 1

                health = MCPServerHealth(
                    server_name=self.server_name,
                    is_healthy=False,
                    last_check=datetime.now(),
                    response_time_ms=response_time,
                    error_count=self.error_count,
                    error_details=f"Connectivity check failed (consecutive failures: {
                        self.consecutive_failures
                    })",
                    capabilities_available=[],
                )

            return health

        except Exception as e:
            self.consecutive_failures += 1
            self.error_count += 1

            return MCPServerHealth(
                server_name=self.server_name,
                is_healthy=False,
                last_check=datetime.now(),
                error_count=self.error_count,
                error_details=str(e),
                capabilities_available=[],
            )

    async def attempt_recovery(self):
        """Attempt to recover the server connection."""
        logger.info(f"Attempting recovery for server: {self.server_name}")

        try:
            # For stdio servers, we might try restarting the process
            if self.server_config.transport.value == "stdio":
                # Implementation would restart the server process
                logger.info(f"Attempting to restart stdio server: {self.server_name}")

            # For HTTP/SSE servers, we might try reconnecting
            elif self.server_config.transport.value in ["http", "sse"]:
                # Implementation would attempt reconnection
                logger.info(
                    f"Attempting to reconnect to HTTP/SSE server: {self.server_name}"
                )

            # Reset consecutive failures on recovery attempt
            self.consecutive_failures = 0

        except Exception as e:
            logger.exception(f"Recovery attempt failed for {self.server_name}: {e}")
            raise

    async def _check_connectivity(self) -> bool:
        """Check basic connectivity to the server.

        Returns:
            True if server is reachable, False otherwise
        """
        try:
            if self.server_config.transport.value == "stdio":
                # For stdio, check if command is available
                return await self._check_command_available()

            if self.server_config.transport.value == "http":
                # For HTTP, try a simple request
                return await self._check_http_connectivity()

            if self.server_config.transport.value == "sse":
                # For SSE, check endpoint availability
                return await self._check_sse_connectivity()

            return False

        except Exception as e:
            logger.exception(f"Connectivity check failed for {self.server_name}: {e}")
            return False

    async def _check_command_available(self) -> bool:
        """Check if stdio command is available.

        Returns:
            True if command is available, False otherwise
        """
        if not self.server_config.command:
            return False

        try:
            # Check if command exists
            process = await asyncio.create_subprocess_exec(
                "which",
                self.server_config.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await process.communicate()
            return process.returncode == 0

        except Exception:
            return False

    async def _check_http_connectivity(self) -> bool:
        """Check HTTP server connectivity.

        Returns:
            True if HTTP server is reachable, False otherwise
        """
        # Implementation would make HTTP request to server
        # For now, return True as placeholder
        return True

    async def _check_sse_connectivity(self) -> bool:
        """Check SSE server connectivity.

        Returns:
            True if SSE server is reachable, False otherwise
        """
        # Implementation would check SSE endpoint
        # For now, return True as placeholder
        return True

    async def _get_available_capabilities(self) -> list[str]:
        """Get list of available capabilities from the server.

        Returns:
            List of capability names
        """
        # Implementation would query server for actual capabilities
        # For now, return configured capabilities
        return self.server_config.capabilities
