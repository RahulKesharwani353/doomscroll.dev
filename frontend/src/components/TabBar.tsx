import { FilterIcon } from '../assets/icons';

type TabType = 'trending' | 'latest' | 'popular';

interface TabBarProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
}

export default function TabBar({ activeTab, onTabChange }: TabBarProps) {
  const tabs: { id: TabType; label: string }[] = [
    { id: 'trending', label: 'Trending' },
    { id: 'latest', label: 'Latest' },
    { id: 'popular', label: 'Popular' },
  ];

  return (
    <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 sm:gap-0 mb-4 sm:mb-6 animate-fade-in">
      {/* Tabs */}
      <div className="flex items-center gap-1 p-1 bg-[rgba(255,255,255,0.05)] border border-[rgba(255,255,255,0.1)] rounded-xl overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`relative px-3 sm:px-[18px] py-2 rounded-lg text-[12px] sm:text-[13px] font-medium transition-all duration-200 cursor-pointer whitespace-nowrap hover:scale-105 active:scale-95 ${
              activeTab === tab.id
                ? 'bg-gradient-to-br from-purple-500 to-indigo-500 text-white shadow-[0px_4px_15px_0px_rgba(168,85,247,0.15)]'
                : 'text-[#a0aec0] hover:text-white hover:bg-white/5'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Filters Button */}
      <button className="flex items-center justify-center sm:justify-start gap-2 px-3.5 py-2 bg-[rgba(255,255,255,0.05)] border border-[rgba(255,255,255,0.1)] rounded-[10px] text-[12px] sm:text-[13px] text-[#a0aec0] hover:text-white hover:bg-[rgba(255,255,255,0.08)] hover:border-[rgba(255,255,255,0.2)] transition-all duration-200 hover:scale-105 active:scale-95 cursor-pointer">
        <FilterIcon className="w-4 h-4" />
        Filters
      </button>
    </div>
  );
}

export type { TabType };
