'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export function TaskLabels({ labels }: { labels: any[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Labels ({labels.length})</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-2">
          {labels.map((lbl) => (
            <span
              key={lbl.id}
              className="px-2.5 py-1 text-xs font-semibold rounded-full text-white"
              style={{ backgroundColor: lbl.color || '#6B7280' }}
            >
              {lbl.name}
            </span>
          ))}
          {labels.length === 0 && (
            <p className="text-sm text-muted-foreground italic">No labels attached.</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
