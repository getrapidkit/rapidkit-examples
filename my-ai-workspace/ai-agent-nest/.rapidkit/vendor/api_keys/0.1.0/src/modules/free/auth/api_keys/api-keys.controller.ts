import {
  Body,
  Controller,
  Get,
  Post,
} from "@nestjs/common";

import { ApiKeysService } from "./api-keys.service";

interface IssueDto {
  ownerId: string;
  scopes?: string[];
  label?: string | null;
  metadata?: Record<string, unknown>;
  ttlHours?: number | null;
}

interface VerifyDto {
  token: string;
  requiredScopes?: string[];
}

interface RevokeDto {
  keyId: string;
  reason?: string | null;
}

@Controller("api-keys")
export class ApiKeysController {
  constructor(private readonly service: ApiKeysService) {}

  @Get("health")
  getHealth(): Record<string, unknown> {
    return this.service.getHealth();
  }

  @Post("issue")
  issue(@Body() payload: IssueDto): Record<string, unknown> {
    return this.service.issue(payload) as unknown as Record<string, unknown>;
  }

  @Post("verify")
  verify(@Body() payload: VerifyDto): Record<string, unknown> {
    return this.service.verify(payload.token, payload.requiredScopes) as unknown as Record<string, unknown>;
  }

  @Post("revoke")
  revoke(@Body() payload: RevokeDto): Record<string, unknown> {
    return this.service.revoke(payload.keyId, payload.reason) as unknown as Record<string, unknown>;
  }
}
