import { Injectable, Logger } from "@nestjs/common";
import OpenAI from "openai";
import { AiAssistantService, AssistantMessage } from "../modules/free/ai/ai_assistant/ai_assistant.service";

export interface SupportTicketResponse {
    ticket_id: string;
    urgency: "low" | "medium" | "high";
    ai_response: string;
    latency_ms: number;
    next_action: "monitor" | "escalate";
    provider: string;
}

@Injectable()
export class SupportAgentService {
    private readonly logger = new Logger(SupportAgentService.name);
    private readonly systemPrompt =
        "You are a helpful customer support agent. Be concise, friendly, and solution-oriented. If you do not know, escalate to human support.";

    constructor(private readonly assistant: AiAssistantService) {
        this.registerOpenAiProviderIfAvailable();
    }

    async handleTicket(message: string): Promise<SupportTicketResponse> {
        const provider = this.resolveProvider();
        const urgency = await this.classifyUrgency(message, provider);

        const context: AssistantMessage[] = provider === "openai" ? [{ role: "system", content: this.systemPrompt }] : [];
        const response = await this.assistant.chat({
            prompt: message,
            provider,
            context,
        });

        return {
            ticket_id: "TKT-12345",
            urgency,
            ai_response: response.content,
            latency_ms: response.latencyMs,
            next_action: urgency === "high" ? "escalate" : "monitor",
            provider,
        };
    }

    private resolveProvider(): string {
        const providers = this.assistant.listProviders();
        if (providers.includes("openai")) {
            return "openai";
        }
        if (providers.includes("support")) {
            return "support";
        }
        return "echo";
    }

    private async classifyUrgency(message: string, provider: string): Promise<"low" | "medium" | "high"> {
        const response = await this.assistant.chat({
            prompt: `Classify urgency (low/medium/high): ${message}`,
            provider,
            settings: { temperature: 0.1 },
        });

        const normalized = response.content.toLowerCase();
        if (normalized.includes("high")) {
            return "high";
        }
        if (normalized.includes("medium")) {
            return "medium";
        }
        return "low";
    }

    private registerOpenAiProviderIfAvailable(): void {
        const apiKey = process.env.OPENAI_API_KEY;
        if (!apiKey || this.assistant.hasProvider("openai")) {
            return;
        }

        try {
            const client = new OpenAI({ apiKey });
            const defaultModel = process.env.OPENAI_MODEL ?? "gpt-4";
            const defaultTemperature = Number(process.env.OPENAI_TEMPERATURE ?? "0.7");

            this.assistant.registerProvider("openai", async (prompt, context, settings) => {
                const messages = context.map((message) => ({
                    role: message.role,
                    content: message.content,
                }));
                messages.push({ role: "user", content: prompt });

                const completion = await client.chat.completions.create({
                    model: typeof settings?.model === "string" ? settings.model : defaultModel,
                    messages,
                    temperature:
                        typeof settings?.temperature === "number" ? settings.temperature : defaultTemperature,
                });

                return completion.choices[0]?.message?.content ?? "";
            });
        } catch (error) {
            this.logger.warn(`Failed to register OpenAI provider: ${String(error)}`);
        }
    }
}
