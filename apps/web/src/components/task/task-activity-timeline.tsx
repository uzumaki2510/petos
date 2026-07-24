'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function TaskActivityTimeline({ activities }: { activities: any[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Activity History ({activities.length})</CardTitle>
      </CardHeader>
      <CardContent>
        <div data-testid="activity-timeline" className="space-y-4 border-l-2 border-muted pl-4">
          {activities.map((act) => (
            <div
              key={act.id}
              data-testid="activity-event"
              data-event-type={act.event_type}
              className="relative text-sm space-y-0.5"
            >
              <div className="absolute -left-[21px] top-1.5 w-2.5 h-2.5 rounded-full bg-primary" />
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span className="font-semibold text-foreground uppercase">{act.event_type}</span>
                <span>{new Date(act.created_at).toLocaleString()}</span>
              </div>
              {act.previous_value && act.new_value && (
                <p className="text-xs text-muted-foreground">
                  {act.previous_value} → <span className="font-semibold text-foreground">{act.new_value}</span>
                </p>
              )}
              {!act.previous_value && act.new_value && (
                <p className="text-xs text-foreground font-medium">{act.new_value}</p>
              )}
              {act.metadata?.reason && (
                <p className="text-xs italic text-muted-foreground">Reason: "{act.metadata.reason}"</p>
              )}
            </div>
          ))}
          {activities.length === 0 && (
            <p className="text-sm text-muted-foreground italic">No activities recorded.</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
