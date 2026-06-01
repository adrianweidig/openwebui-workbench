from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
WIZARD = ROOT / "Deployment" / "configure-workbench-enterprise.ps1"
POWERSHELL = shutil.which("powershell") or shutil.which("pwsh")


class ConfigureWorkbenchEnterpriseTests(unittest.TestCase):
    def test_generated_portainer_stack_requires_workbench_password(self) -> None:
        script = WIZARD.read_text(encoding="utf-8")

        self.assertIn(
            "WORKBENCH_AUTH_PASSWORD: `${WORKBENCH_AUTH_PASSWORD:?Set WORKBENCH_AUTH_PASSWORD",
            script,
        )
        self.assertNotIn("WORKBENCH_AUTH_PASSWORD: `${WORKBENCH_AUTH_PASSWORD:-}", script)

    def test_generated_portainer_stack_sets_safe_automation_defaults(self) -> None:
        script = WIZARD.read_text(encoding="utf-8")

        self.assertIn("WORKBENCH_AUTOMATION_ENABLED=true", script)
        self.assertIn("WORKBENCH_AUTOMATION_INTERVAL_MINUTES=30", script)
        self.assertIn("WORKBENCH_AUTOMATION_ACTIONS=check", script)
        self.assertIn("WORKBENCH_AUTOMATION_INTERVAL_MINUTES: `${WORKBENCH_AUTOMATION_INTERVAL_MINUTES:-30}", script)
        self.assertIn("WORKBENCH_AUTOMATION_ACTIONS: `${WORKBENCH_AUTOMATION_ACTIONS:-check}", script)

    def test_generated_portainer_stack_supports_existing_docker_network(self) -> None:
        script = WIZARD.read_text(encoding="utf-8")

        self.assertIn('[string]$DockerNetworkName = "openwebui-workbench_workbench"', script)
        self.assertIn("[switch]$UseExternalDockerNetwork", script)
        self.assertIn("WORKBENCH_DOCKER_NETWORK=$DockerNetworkName", script)
        self.assertIn('"    external: true"', script)
        self.assertIn('"    name: `${WORKBENCH_DOCKER_NETWORK}"', script)
        self.assertIn('"    name: `${WORKBENCH_DOCKER_NETWORK:-openwebui-workbench_workbench}"', script)

    def test_remote_root_ca_paths_require_explicit_opt_in(self) -> None:
        script = WIZARD.read_text(encoding="utf-8")

        self.assertIn("[switch]$AllowUnverifiedRootCaPath", script)
        self.assertIn("-AllowUnverified:$AllowUnverifiedRootCaPath", script)
        self.assertIn("Root-CA-Datei ist lokal nicht lesbar", script)
        self.assertIn("-AllowUnverifiedRootCaPath", script)

    @unittest.skipUnless(POWERSHELL, "PowerShell is required for wizard generation smoke")
    def test_existing_mode_does_not_emit_unused_openwebui_volume(self) -> None:
        assert POWERSHELL is not None
        with tempfile.TemporaryDirectory() as tmpdir:
            subprocess.run(
                [
                    POWERSHELL,
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(WIZARD),
                    "-NonInteractive",
                    "-OpenWebUIMode",
                    "existing",
                    "-OpenWebUIBaseUrl",
                    "http://openwebui:8080",
                    "-OpenWebUIPublicUrl",
                    "http://localhost:3000",
                    "-UseExternalDockerNetwork",
                    "-DockerNetworkName",
                    "shared_ai_net",
                    "-OutputDir",
                    tmpdir,
                ],
                check=True,
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            compose = (Path(tmpdir) / "portainer-compose.yml").read_text(encoding="utf-8")

        self.assertNotIn("  openwebui:", compose)
        self.assertNotIn("openwebui-data:", compose)
        self.assertIn("    external: true", compose)
        self.assertIn("    name: ${WORKBENCH_DOCKER_NETWORK}", compose)

    @unittest.skipUnless(POWERSHELL, "PowerShell is required for wizard generation smoke")
    def test_unverified_remote_root_ca_path_is_written_when_explicitly_allowed(self) -> None:
        assert POWERSHELL is not None
        remote_ca_path = "/opt/company-ca/openwebui-root-ca.pem"
        with tempfile.TemporaryDirectory() as tmpdir:
            subprocess.run(
                [
                    POWERSHELL,
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(WIZARD),
                    "-NonInteractive",
                    "-RootCaPath",
                    remote_ca_path,
                    "-AllowUnverifiedRootCaPath",
                    "-OutputDir",
                    tmpdir,
                ],
                check=True,
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            env_text = (Path(tmpdir) / "workbench.env").read_text(encoding="utf-8")

        self.assertIn(f"WORKBENCH_ENTERPRISE_CA_HOST_FILE={remote_ca_path}", env_text)
        self.assertIn("OPENWEBUI_CA_FILE=/certs/company-root-ca.pem", env_text)

    @unittest.skipUnless(POWERSHELL, "PowerShell is required for wizard generation smoke")
    def test_unverified_remote_root_ca_path_fails_without_opt_in(self) -> None:
        assert POWERSHELL is not None
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                [
                    POWERSHELL,
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(WIZARD),
                    "-NonInteractive",
                    "-RootCaPath",
                    "/opt/company-ca/not-mounted-here.pem",
                    "-OutputDir",
                    tmpdir,
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Root-CA-Datei ist lokal nicht lesbar", result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
