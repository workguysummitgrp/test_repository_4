"use client";

import Link from "next/link";
import { ArrowRight, Shield, Zap, Brain } from "lucide-react";

export default function HomePage() {
  return (
    <main className="flex flex-col items-center justify-center min-h-screen px-4">
      <div className="max-w-3xl text-center space-y-6">
        <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl">
          AI-Powered Customer Onboarding
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Submit your application and get evaluated by our intelligent system
          for fast, fair, and transparent onboarding decisions.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center mt-8">
          <Link
            href="/register"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-primary-600 text-white font-medium hover:bg-primary-700 transition-colors"
          >
            Get Started <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            href="/login"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-lg border border-gray-300 text-gray-700 font-medium hover:bg-gray-100 transition-colors"
          >
            Sign In
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mt-16">
          <div className="p-6 rounded-xl bg-white border border-gray-200 text-left">
            <Zap className="w-8 h-8 text-primary-600 mb-3" />
            <h3 className="font-semibold text-gray-900">Fast Processing</h3>
            <p className="text-sm text-gray-500 mt-1">
              AI evaluates your application in seconds, not days.
            </p>
          </div>
          <div className="p-6 rounded-xl bg-white border border-gray-200 text-left">
            <Brain className="w-8 h-8 text-primary-600 mb-3" />
            <h3 className="font-semibold text-gray-900">Intelligent Scoring</h3>
            <p className="text-sm text-gray-500 mt-1">
              GPT-4o powered evaluation with structured scoring.
            </p>
          </div>
          <div className="p-6 rounded-xl bg-white border border-gray-200 text-left">
            <Shield className="w-8 h-8 text-primary-600 mb-3" />
            <h3 className="font-semibold text-gray-900">Full Audit Trail</h3>
            <p className="text-sm text-gray-500 mt-1">
              Every action is logged for compliance and transparency.
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
