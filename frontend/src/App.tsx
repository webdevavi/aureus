import { Sparkles } from "lucide-react";
import { useState } from "react";
import { CreateReport } from "./components/reports/create-report";
import { ReportItemModal } from "./components/reports/report-item-modal";
import { ReportItems } from "./components/reports/report-items";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "./components/ui/card";
import type { Report } from "./types/report";
import { HeroGeometric } from "./components/ui/shape-landing-hero";

function App() {
  const [selectedReport, setSelectedReport] = useState<Report>();

  return (
    <HeroGeometric
      heading="Automate Research Intelligence"
      description="Turn complex PDFs into structured financial insights — instantly."
    >
      <Card className="w-full max-w-4xl shadow-2xl rounded-3xl overflow-hidden border border-border/80 backdrop-blur-xl bg-background/70">
        <CardHeader className="border-b border-border/40 px-6 sm:px-8 py-4 sm:py-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex flex-col items-start">
              <CardTitle className="text-2xl mb-1 font-semibold">
                Reports Workspace
              </CardTitle>
              <p className="text-sm text-muted-foreground font-medium">
                Manage extracted data, verify AI outputs, and monitor report
                processing.
              </p>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-secondary/70 rounded-full border border-secondary/40 backdrop-blur-md">
              <Sparkles className="w-4 h-4 text-primary" />
              <span className="text-xs font-semibold text-primary">
                Live Sync
              </span>
            </div>
          </div>
        </CardHeader>

        <CardContent className="p-6 sm:p-8">
          <ReportItems onSelectReport={setSelectedReport} />
        </CardContent>

        <CardFooter className="border-t border-border/40 px-6 sm:px-8 py-6 flex flex-col items-stretch">
          <CreateReport onCreated={(report) => setSelectedReport(report)} />
        </CardFooter>
      </Card>

      <footer className="py-8 text-center space-y-1">
        <p className="text-xs text-muted-foreground tracking-wide">
          © {new Date().getFullYear()} Aureus. All rights reserved.
        </p>
        <p className="text-[11px] text-muted-foreground/80">
          Built for financial analysts who demand accuracy, transparency, and
          automation.
        </p>
      </footer>

      {selectedReport && (
        <ReportItemModal
          report={selectedReport}
          onClose={() => setSelectedReport(undefined)}
        />
      )}
    </HeroGeometric>
  );
}

export default App;
