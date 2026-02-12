import { Controller, Get } from '@nestjs/common';

import { DeploymentService } from './deployment.service';

@Controller('deployment')
export class DeploymentController {
  constructor(private readonly service: DeploymentService) {}

  @Get('plan')
  getPlan() {
    return this.service.describePlan();
  }

  @Get('assets')
  listAssets() {
    return this.service.listAssets();
  }
}
