import { BASE_API_URL } from "@/config/settings";
import { useMutation } from "@tanstack/react-query";
import type { FileType, FileCategory } from "@/types/report-file";

export const useCreatePresignedUploadUrl = (report_id: number) => {
  return useMutation<
    {
      file_id: number;
      upload_url: string;
      s3_key: string;
      s3_bucket: string;
      file_type: FileType;
      category: FileCategory;
      status: string;
    },
    Error,
    {
      file_type: FileType;
      category: FileCategory;
    }
  >({
    mutationKey: ["create-presigned-upload-url", report_id.toString()],
    mutationFn: async ({ file_type, category }) => {
      const response = await fetch(
        `${BASE_API_URL}/reports/${report_id}/files/upload?file_type=${file_type}&category=${category}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        }
      );

      if (!response.ok) {
        const text = await response.text();
        throw new Error(
          `Failed to create presigned upload URL: ${response.status} - ${text}`
        );
      }

      return response.json();
    },
  });
};
