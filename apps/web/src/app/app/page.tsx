import { Metadata } from 'next';
import { getUserOrganizations, getOrganizationProjects } from '@/lib/api/server';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button, buttonVariants } from '@/components/ui/button';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Dashboard | PetOS',
};

export default async function DashboardPage() {
  // Server Component data fetching
  let organizations: any[] = [];
  let projects: any[] = [];

  try {
    organizations = await getUserOrganizations();
    if (organizations.length > 0) {
      const firstOrg = organizations[0];
      projects = await getOrganizationProjects(firstOrg.id);
    }
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error);
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Your Workspace</h1>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {organizations.length > 0 && (
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Active Organization
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{organizations[0].name}</div>
              <p className="text-xs text-muted-foreground">
                Role: Owner
              </p>
            </CardContent>
          </Card>
        )}
      </div>

      <div className="mt-8">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold">Projects</h2>
          {organizations.length > 0 && (
            <Link href={`/app/projects/new?orgId=${organizations[0].id}`} className={buttonVariants({ size: "sm" })}>
              New Project
            </Link>
          )}
        </div>

        {projects.length === 0 ? (
          <div className="rounded-md border border-dashed p-8 text-center">
            <h3 className="mt-2 text-sm font-semibold text-gray-900 dark:text-gray-100">No projects</h3>
            <p className="mt-1 text-sm text-gray-500">Get started by creating a new project.</p>
            <div className="mt-6">
              {organizations.length > 0 && (
                <Link href={`/app/projects/new?orgId=${organizations[0].id}`} className={buttonVariants()}>
                  Create Project
                </Link>
              )}
            </div>
          </div>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {projects.map((project: any) => (
              <Card key={project.id}>
                <CardHeader>
                  <CardTitle>{project.name}</CardTitle>
                  <CardDescription className="truncate">
                    {project.description || 'No description'}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Link href={`/app/projects/${project.id}`} className="text-sm text-primary hover:underline">
                    View Project
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
