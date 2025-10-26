import { BASE_API_URL } from "@/config/settings";
import type { Report } from "@/types/report";
import { useMutation } from "@tanstack/react-query";

export const useCreateReport = () => {
  return useMutation<Report, Error, string>({
    mutationKey: ["create-report"],
    mutationFn: async (companyName: string) => {
      const response = await fetch(
        `${BASE_API_URL}/reports?company_name=${companyName}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        }
      );

      return response.json() as unknown as Report;
    },
  });
};
