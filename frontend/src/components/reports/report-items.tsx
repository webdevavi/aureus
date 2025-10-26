import { useGetReports } from "@/api/queries/use-get-reports";
import type { Report } from "@/types/report";
import { AlertTriangle, ClipboardIcon, RefreshCcw } from "lucide-react";
import React, { useEffect, useRef } from "react";
import { Button } from "../ui/button";
import {
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "../ui/empty";
import { ItemGroup } from "../ui/item";
import { ScrollArea, ScrollBar } from "../ui/scroll-area";
import { Skeleton } from "../ui/skeleton";
import { ReportItem } from "./report-item";

interface ReportItemsProps {
  onSelectReport?: (report: Report) => void;
}

export const ReportItems: React.FC<ReportItemsProps> = ({ onSelectReport }) => {
  const { data, isLoading, isError, refetch } = useGetReports();

  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!data?.length) return;

    const tryScroll = () => {
      const viewport = scrollAreaRef.current?.querySelector(
        "[data-radix-scroll-area-viewport]"
      ) as HTMLElement | null;

      if (!viewport) return;

      const hasContent = viewport.scrollHeight > viewport.clientHeight;
      if (hasContent) {
        viewport.scrollTo({ top: viewport.scrollHeight, behavior: "smooth" });
        return true;
      }
      return false;
    };

    let tries = 0;
    const interval = setInterval(() => {
      const success = tryScroll();
      tries++;
      if (success || tries > 20) clearInterval(interval);
    }, 150);

    return () => clearInterval(interval);
  }, [data]);

  if (isLoading) {
    return (
      <ScrollArea className="h-96">
        <ItemGroup className="gap-2">
          {Array.from({ length: 2 }).map((_, i) => (
            <div
              key={i}
              className="p-3 border rounded-md flex flex-col gap-2 animate-pulse"
            >
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-3 w-1/2" />
            </div>
          ))}
        </ItemGroup>
      </ScrollArea>
    );
  }

  if (isError) {
    return (
      <Empty>
        <EmptyHeader>
          <EmptyMedia variant="icon">
            <AlertTriangle />
          </EmptyMedia>
          <EmptyTitle>Failed to load reports</EmptyTitle>
          <EmptyDescription>
            Something went wrong while fetching your reports. Please try again.
          </EmptyDescription>
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            <RefreshCcw className="w-4 h-4 mr-1" />
            Retry
          </Button>
        </EmptyHeader>
      </Empty>
    );
  }

  if (!data?.length) {
    return (
      <Empty>
        <EmptyHeader>
          <EmptyMedia variant="icon">
            <ClipboardIcon />
          </EmptyMedia>
          <EmptyTitle>No reports yet</EmptyTitle>
          <EmptyDescription>
            You haven&apos;t created any reports yet. Create your first one
            below.
          </EmptyDescription>
        </EmptyHeader>
      </Empty>
    );
  }

  return (
    <ScrollArea ref={scrollAreaRef} className="h-96">
      <ItemGroup className="gap-2">
        {data.map((report) => (
          <ReportItem
            key={report.id}
            report={report}
            onSelect={onSelectReport}
          />
        ))}
      </ItemGroup>
      <ScrollBar />
    </ScrollArea>
  );
};
