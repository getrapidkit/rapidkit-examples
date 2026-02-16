import { INestApplication } from '@nestjs/common';
import { Test, TestingModule } from '@nestjs/testing';
import request from 'supertest';

import { AppModule } from '../src/app.module';

describe('SaaS Nest routes (e2e)', () => {
    let app: INestApplication;

    beforeAll(async () => {
        const moduleFixture: TestingModule = await Test.createTestingModule({
            imports: [AppModule],
        }).compile();

        app = moduleFixture.createNestApplication();
        await app.init();
    });

    afterAll(async () => {
        await app.close();
    });

    it('register/login/me/profile flow', async () => {
        const server = app.getHttpServer();
        const registerEmail = `nest-${Date.now()}@example.com`;

        const register = await request(server)
            .post('/auth/register')
            .send({ email: registerEmail, password: 'StrongPass123!', fullName: 'Nest User' })
            .expect(201);

        expect(register.body.user.email).toBe(registerEmail);
        expect(register.body.access_token).toBeDefined();

        const login = await request(server)
            .post('/auth/login')
            .send({ email: registerEmail, password: 'StrongPass123!' })
            .expect(200);

        const token = login.body.access_token as string;
        expect(token).toBeDefined();

        await request(server).get('/auth/me').set('Authorization', `Bearer ${token}`).expect(200);

        const profile = await request(server)
            .get('/users/profile')
            .set('Authorization', `Bearer ${token}`)
            .expect(200);

        expect(profile.body.userId).toBeDefined();

        const updated = await request(server)
            .put('/users/profile')
            .set('Authorization', `Bearer ${token}`)
            .send({ displayName: 'Updated User', timezone: 'UTC', biography: 'Nest profile' })
            .expect(200);

        expect(updated.body.displayName).toBe('Updated User');
    });
});
