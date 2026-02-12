import { registerAs } from '@nestjs/config';

type PackageManager = 'npm' | 'pnpm' | 'yarn';

type DeploymentConfig = {
  includeCi: boolean;
  includePostgres: boolean;
  pythonVersion: string;
  nodeVersion: string;
  packageManager: PackageManager;
  packageManagerCommand: string;
};

export default registerAs('deployment', (): DeploymentConfig => ({
  includeCi: true,
  includePostgres: true,
  pythonVersion: "3.10.14",
  nodeVersion: "20.19.6",
  packageManager: "npm",
  packageManagerCommand: "npm",
}));
