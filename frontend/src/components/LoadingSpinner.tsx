import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  message?: string;
}

export default function LoadingSpinner({ message = "Loading..." }: LoadingSpinnerProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <Loader2 size={40} className="text-tbank-yellow animate-spin mb-4" />
      <p className="text-tbank-gray">{message}</p>
    </div>
  );
}

