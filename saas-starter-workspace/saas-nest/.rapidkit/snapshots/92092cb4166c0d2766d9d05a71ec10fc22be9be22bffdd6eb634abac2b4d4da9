import { INestApplication } from '@nestjs/common';
import { Test } from '@nestjs/testing';
import request from 'supertest';

import { SecurityHeadersModule } from '../../../../src/modules/free/security/security_headers/security-headers/security-headers.module';
import { SecurityHeadersHealthModule } from '../../../../src/health/security-headers-health.module';
import { SecurityHeadersService } from '../../../../src/modules/free/security/security_headers/security-headers/security-headers.service';

async function createApplication(): Promise<INestApplication> {
  const moduleRef = await Test.createTestingModule({
    imports: [SecurityHeadersModule, SecurityHeadersHealthModule],
  }).compile();

  const app = moduleRef.createNestApplication();
  await app.init();
  return app;
}

describe('SecurityHeadersModule (Integration)', () => {
  let app: INestApplication;
  let service: SecurityHeadersService;

  beforeAll(async () => {
    app = await createApplication();
    service = app.get(SecurityHeadersService);
  });

  afterAll(async () => {
    await app.close();
  });

  it('exposes service bindings', () => {
    expect(service).toBeDefined();
    const health = service.health();
    expect(health).toHaveProperty('module', "security_headers");
    expect(service.getHeaders()).toBeDefined();
  });

  it('serves module health endpoint', async () => {
    const server = app.getHttpServer();
    const response = await request(server).get('/api/health/module/security-headers');

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('module', "security_headers");
    expect(response.body).toHaveProperty('status');
  });
});
