import { getProject } from '@/lib/api/server';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { buttonVariants } from '@/components/ui/button';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { Metadata } from 'next';

export async function generateMetadata({ params }: { params: Promise<{ projectId: string }> }): Promise<Metadata> {
  const resolvedParams = await params;
  try {
    const project = await getProject(resolvedParams.projectId);
    return {
      title: `${project?.name || 'Project'} | PetOS`,
    };
  } catch {
    return {
      title: 'Project | PetOS',
    };
  }
}

export default async function ProjectPage({ params }: { params: Promise<{ projectId: string }> }) {
  const resolvedParams = await params;
  let project: any;
  try {
    project = await getProject(resolvedParams.projectId);
    if (!project) {
      notFound();
    }
  } catch (error) {
    notFound();
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{project.name}</h1>
          <p className="text-muted-foreground mt-2">{project.description || 'No description'}</p>
        </div>
        <Link href="/app/projects" id="back-to-projects" className={buttonVariants({ variant: "outline" })}>
          Back
        </Link>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Project Details</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div>
                <span className="text-sm font-medium text-muted-foreground">ID: </span>
                <span className="text-sm font-mono">{project.id}</span>
              </div>
              <div>
                <span className="text-sm font-medium text-muted-foreground">Slug: </span>
                <span className="text-sm font-mono">{project.slug}</span>
              </div>
              <div>
                <span className="text-sm font-medium text-muted-foreground">Status: </span>
                <span className="text-sm capitalize">{project.status}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
