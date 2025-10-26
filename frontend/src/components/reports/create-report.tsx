import { useCreateReport } from "@/api/mutations/use-create-report";
import { queryClient } from "@/api/query-client";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import type { Report } from "@/types/report";
import { zodResolver } from "@hookform/resolvers/zod";
import React from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Loader2 } from "lucide-react";

const formSchema = z.object({
  companyName: z.string().min(2, {
    message: "Company name must be at least 2 characters.",
  }),
});

type FormValues = z.infer<typeof formSchema>;

export interface CreateReportProps {
  onCreated?: (report: Report) => void;
}

export const CreateReport: React.FC<CreateReportProps> = ({ onCreated }) => {
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { companyName: "" },
  });

  const { mutateAsync, isPending } = useCreateReport();

  const onSubmit = async (values: FormValues) => {
    try {
      const report = await mutateAsync(values.companyName);
      form.reset();
      queryClient.setQueryData(["reports"], (oldData: any) => [
        ...(oldData || []),
        report,
      ]);
      onCreated?.(report);
    } catch {
      form.setError("companyName", {
        type: "server",
        message: "Failed to create report. Please try again.",
      });
    }
  };

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className="flex flex-col gap-3"
      >
        <FormField
          control={form.control}
          name="companyName"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Create New Report</FormLabel>
              <FormControl>
                <Input
                  placeholder="Enter a company name"
                  {...field}
                  disabled={isPending}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button
          type="submit"
          disabled={isPending}
          className="self-start flex items-center gap-2"
        >
          {isPending && (
            <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
          )}
          {isPending ? "Creating..." : "Create"}
        </Button>
      </form>
    </Form>
  );
};
