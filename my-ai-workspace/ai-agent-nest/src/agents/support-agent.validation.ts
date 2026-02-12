import { IsNotEmpty, IsString, MaxLength } from "class-validator";

export class SupportTicketRequestDto {
    @IsString()
    @IsNotEmpty()
    @MaxLength(4000)
    message!: string;
}
