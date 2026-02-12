import { Body, Controller, Get, Post } from '@nestjs/common';
import { AppService } from './app.service';
import { SupportTicketRequestDto } from './agents/support-agent.validation';
import { SupportAgentService, SupportTicketResponse } from './agents/support-agent.service';

@Controller()
export class AppController {
  constructor(
    private readonly appService: AppService,
    private readonly supportAgentService: SupportAgentService,
  ) {}

  @Get('health')
  getHealth() {
    return this.appService.getHealth();
  }

  @Post('support/ticket')
  async handleSupportTicket(@Body() payload: SupportTicketRequestDto): Promise<SupportTicketResponse> {
    return this.supportAgentService.handleTicket(payload.message);
  }

  // <<<inject:controller-routes>>>
}