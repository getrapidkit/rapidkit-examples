import {
    Body,
    Controller,
    Get,
    Headers,
    HttpException,
    HttpStatus,
    Put,
} from '@nestjs/common';

import { AuthService } from './auth.service';

@Controller('users')
export class UsersController {
    constructor(private readonly authService: AuthService) { }

    @Get('profile')
    profile(@Headers('authorization') authorization?: string) {
        const token = extractBearer(authorization);
        if (!token) {
            throw new HttpException('Authentication required', HttpStatus.UNAUTHORIZED);
        }

        const profile = this.authService.getProfile(token);
        if (!profile) {
            throw new HttpException('Profile not found', HttpStatus.NOT_FOUND);
        }
        return profile;
    }

    @Put('profile')
    upsertProfile(
        @Body() payload: { displayName?: string; timezone?: string; biography?: string },
        @Headers('authorization') authorization?: string,
    ) {
        const token = extractBearer(authorization);
        if (!token) {
            throw new HttpException('Authentication required', HttpStatus.UNAUTHORIZED);
        }

        const profile = this.authService.updateProfile(token, payload);
        if (!profile) {
            throw new HttpException('Invalid token', HttpStatus.UNAUTHORIZED);
        }
        return profile;
    }
}

function extractBearer(authorization?: string): string | null {
    if (!authorization || !authorization.toLowerCase().startsWith('bearer ')) {
        return null;
    }
    return authorization.split(' ', 2)[1] ?? null;
}
