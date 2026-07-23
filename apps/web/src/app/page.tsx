import StatusDisplay from "@/components/StatusDisplay";

export const metadata = {
  title: "PetOS - Phase 2: Engineering Foundation",
  description: "Engineering foundation status page for PetOS",
};

export default function Home() {
  return (
    <main className="min-h-screen p-8 bg-gray-50 text-gray-900 font-sans">
      <header className="max-w-3xl mx-auto mb-8 border-b pb-4">
        <h1 className="text-4xl font-bold text-blue-900 tracking-tight">PetOS</h1>
        <p className="text-xl text-gray-600 mt-2 font-medium">Phase 2: Engineering Foundation</p>
      </header>
      <section className="max-w-3xl mx-auto">
        <h2 className="text-2xl font-semibold mb-6">System Status</h2>
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <StatusDisplay />
        </div>
      </section>
    </main>
  );
}
