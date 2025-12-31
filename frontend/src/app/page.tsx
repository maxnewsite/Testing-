import Link from 'next/link'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gradient-to-b from-blue-50 to-white">
      <div className="max-w-4xl w-full text-center space-y-8">
        <h1 className="text-6xl font-bold text-gray-900">
          PickFu Market Research
        </h1>
        <p className="text-xl text-gray-600">
          Get instant feedback from real consumers. Create polls, gather insights, and make data-driven decisions.
        </p>

        <div className="flex gap-4 justify-center mt-8">
          <Link
            href="/login"
            className="px-8 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition"
          >
            Sign In
          </Link>
          <Link
            href="/register"
            className="px-8 py-3 bg-white text-blue-600 border-2 border-blue-600 rounded-lg font-semibold hover:bg-blue-50 transition"
          >
            Get Started
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16">
          <div className="p-6 bg-white rounded-lg shadow-md">
            <h3 className="text-xl font-bold mb-2">For Researchers</h3>
            <p className="text-gray-600">
              Create polls, target specific demographics, and get real-time insights from our quality panel.
            </p>
          </div>
          <div className="p-6 bg-white rounded-lg shadow-md">
            <h3 className="text-xl font-bold mb-2">For Panel Members</h3>
            <p className="text-gray-600">
              Earn money by sharing your opinions. Get paid for every validated response you submit.
            </p>
          </div>
          <div className="p-6 bg-white rounded-lg shadow-md">
            <h3 className="text-xl font-bold mb-2">Quality Guaranteed</h3>
            <p className="text-gray-600">
              AI-powered quality checks ensure you get high-quality, reliable data every time.
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}
