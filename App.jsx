import React, { useState } from 'react';
import { Search, Bell, ShieldAlert, ChevronLeft, ChevronRight, ThumbsUp, ThumbsDown, Flag } from 'lucide-react';

const GENRES = ["Action", "Adventure", "Boys Love", "Comedy", "Crime", "Drama", "Fantasy", "Girls' Love", "Historical", "Horror", "Isekai", "Magical Girls", "Mecha", "Medical", "Mystery", "Philosophical", "Psychological", "Romance", "Sci-Fi", "Slice of Life", "Sports", "Superhero", "Thriller", "Tragedy", "Wuxia"];
const THEMES = ["Aliens", "Animals", "Cooking", "Crossdressing", "Delinquents", "Demons", "Genderswap", "Ghosts", "Gyaru", "Harem", "Incest", "Loli", "Mafia", "Magic", "Mahjong", "Martial Arts", "Military", "Monster Girls", "Monsters", "Music", "Ninja", "Office Workers", "Police", "Post-Apocalyptic", "Reincarnation", "Reverse Harem", "Samurai", "School Life", "Shota", "Supernatural", "Survival", "Time Travel", "Traditional Games", "Vampires", "Video Games", "Villainess", "Virtual Reality", "Zombies"];
const WARNINGS = ["Gore", "Sexual Violence"];

export default function SweetBreezeApp() {
  const [mangas, setMangas] = useState([]);

  useEffect(() => {
    fetch('https://sweet-breeze-2.onrender.com/api/manga')
      .then(res => res.json())
      .then(data => setMangas(data))
      .catch(err => console.error("Error fetching data:", err));
  }, []);

  const [activeTab, setActiveTab] = useState('home');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRatings, setSelectedRatings] = useState(['Safe']);
  const [selectedGenres, setSelectedGenres] = useState([]);
  const [showReportModal, setShowReportModal] = useState(false);
  const [agreedToRules, setAgreedToRules] = useState(false);
  const [currentChapter, setCurrentChapter] = useState(1);

  const toggleFilter = (item, list, setList) => {
    setList(list.includes(item) ? list.filter(i => i !== item) : [...list, item]);
  };

  return (
    <div className="min-h-screen bg-[#0D0D0D] text-white font-sans">
      <header className="sticky top-0 z-50 bg-[#0D0D0D]/90 backdrop-blur-md border-b border-red-900/30 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-8">
          <h1 className="text-2xl font-black tracking-wider text-[#E50914] uppercase cursor-pointer">Sweet Breeze</h1>
          <nav className="hidden md:flex space-x-6 text-sm font-medium">
            <a onClick={() => setActiveTab('home')} className="hover:text-[#E50914] cursor-pointer transition">Home</a>
            <a onClick={() => setActiveTab('follows')} className="hover:text-[#E50914] cursor-pointer transition">My Follows</a>
            <a onClick={() => setActiveTab('lists')} className="hover:text-[#E50914] cursor-pointer transition">My Lists</a>
            <a onClick={() => setActiveTab('favorites')} className="hover:text-[#E50914] cursor-pointer transition">Favorites</a>
          </nav>
        </div>

        <div className="relative flex-1 max-w-md mx-6">
          <Search className="absolute left-3 top-2.5 text-gray-400 h-4 w-4" />
          <input
            type="text"
            placeholder="Search titles, authors, tags..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-[#1A1A1A] text-sm text-white pl-10 pr-4 py-2 rounded-full border border-gray-800 focus:outline-none focus:border-[#E50914]"
          />
        </div>

        <div className="flex items-center space-x-4">
          <button className="relative p-2 rounded-full hover:bg-gray-800 text-gray-300">
            <Bell className="h-5 w-5" />
            <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-[#E50914] animate-pulse"></span>
          </button>
          
          <div className="group relative cursor-pointer">
            <img src="https://via.placeholder.com/40" alt="Avatar" className="w-9 h-9 rounded-full border-2 border-[#E50914]" />
            <div className="absolute right-0 mt-2 w-48 bg-[#1A1A1A] border border-gray-800 rounded-lg shadow-xl opacity-0 group-hover:opacity-100 transition-all pointer-events-none group-hover:pointer-events-auto py-2 z-50">
              <a className="block px-4 py-2 text-sm hover:bg-[#E50914] transition">My Profile</a>
              <a className="block px-4 py-2 text-sm hover:bg-[#E50914] transition">My Follows</a>
              <a className="block px-4 py-2 text-sm hover:bg-[#E50914] transition">My Lists</a>
              <a className="block px-4 py-2 text-sm hover:bg-[#E50914] transition">Settings</a>
              <a className="block px-4 py-2 text-sm hover:bg-[#E50914] transition">Content Filter</a>
              <hr className="border-gray-800 my-1" />
              <a className="block px-4 py-2 text-sm text-red-500 hover:bg-red-950 transition">Sign Out</a>
            </div>
          </div>
        </div>
      </header>

      <main className="px-6 py-8 grid grid-cols-1 lg:grid-cols-4 gap-8">
        <aside className="lg:col-span-1 bg-[#141414] p-5 rounded-xl border border-gray-800 space-y-6 h-fit">
          <h2 className="text-lg font-bold text-[#E50914] uppercase tracking-wide">Filters</h2>
          
          <div>
            <label className="text-xs text-gray-400 font-semibold uppercase">Content Rating</label>
            <div className="flex flex-wrap gap-2 mt-2">
              {['Safe', 'Suggestive', 'Erotica'].map(rating => (
                <button
                  key={rating}
                  onClick={() => toggleFilter(rating, selectedRatings, setSelectedRatings)}
                  className={`text-xs px-3 py-1.5 rounded-md border transition ${
                    selectedRatings.includes(rating) 
                      ? 'bg-[#E50914] border-[#E50914] text-white' 
                      : 'border-gray-800 bg-[#1A1A1A] text-gray-400 hover:border-gray-600'
                  }`}
                >
                  {rating}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="text-xs text-gray-400 font-semibold uppercase">Genres</label>
            <div className="flex flex-wrap gap-1.5 mt-2 max-h-48 overflow-y-auto pr-1">
              {GENRES.map(genre => (
                <button
                  key={genre}
                  onClick={() => toggleFilter(genre, selectedGenres, setSelectedGenres)}
                  className={`text-[11px] px-2 py-1 rounded border ${
                    selectedGenres.includes(genre)
                      ? 'bg-[#E50914] border-[#E50914] text-white'
                      : 'border-gray-800 bg-[#1A1A1A] text-gray-400 hover:border-gray-600'
                  }`}
                >
                  {genre}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="text-xs text-red-500 font-semibold uppercase flex items-center gap-1">
              <ShieldAlert className="w-3 h-3" /> Content Warnings
            </label>
            <div className="flex flex-wrap gap-2 mt-2">
              {WARNINGS.map(warning => (
                <span key={warning} className="text-xs px-2.5 py-1 rounded bg-red-950/40 border border-red-900/50 text-red-400">
                  {warning}
                </span>
              ))}
            </div>
          </div>
        </aside>

        <section className="lg:col-span-3 space-y-8">
          <div className="bg-[#141414] p-4 rounded-xl border border-gray-800 flex items-center justify-between">
            <button 
              disabled={currentChapter <= 1}
              onClick={() => setCurrentChapter(c => c - 1)}
              className="flex items-center gap-1 text-sm bg-[#1A1A1A] px-4 py-2 rounded-lg border border-gray-800 hover:border-[#E50914] disabled:opacity-40"
            >
              <ChevronLeft className="w-4 h-4" /> Previous Chapter
            </button>
            <span className="font-semibold text-sm">Chapter {currentChapter}</span>
            <button 
              onClick={() => setCurrentChapter(c => c + 1)}
              className="flex items-center gap-1 text-sm bg-[#1A1A1A] px-4 py-2 rounded-lg border border-gray-800 hover:border-[#E50914]"
            >
              Next Chapter <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          <div className="bg-[#000000] border border-gray-900 rounded-xl min-h-[400px] flex items-center justify-center text-gray-600">
            [ Chapter {currentChapter} Manga Page Viewer ]
          </div>

          <div className="bg-[#141414] p-6 rounded-xl border border-gray-800 space-y-6">
            <h3 className="text-lg font-bold border-b border-gray-800 pb-3">Comments</h3>

            <div className="space-y-3">
              <textarea 
                rows="3" 
                placeholder="Leave a comment... (Requires login)" 
                className="w-full bg-[#1A1A1A] text-sm text-white p-3 rounded-lg border border-gray-800 focus:outline-none focus:border-[#E50914]"
              />
              <button className="bg-[#E50914] text-white px-5 py-2 rounded-lg text-sm font-semibold hover:bg-red-700 transition">
                Post Comment
              </button>
            </div>

            <div className="space-y-4 pt-4">
              <div className="bg-[#1A1A1A] p-4 rounded-lg border border-gray-800/60 flex space-x-4">
                <img src="https://via.placeholder.com/36" alt="User" className="w-9 h-9 rounded-full border border-[#E50914]" />
                <div className="flex-1 space-y-1">
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-bold text-gray-300">OtakuReader_99</span>
                    <span className="text-[10px] text-gray-500">2 hours ago</span>
                  </div>
                  <p className="text-sm text-gray-300">This chapter was incredible! The cliffhanger at the end blew my mind.</p>
                  
                  <div className="flex items-center space-x-4 pt-2 text-xs text-gray-400">
                    <button className="flex items-center gap-1 hover:text-[#E50914]"><ThumbsUp className="w-3.5 h-3.5" /> 24</button>
                    <button className="flex items-center gap-1 hover:text-gray-200"><ThumbsDown className="w-3.5 h-3.5" /> 2</button>
                    <button onClick={() => setShowReportModal(true)} className="flex items-center gap-1 hover:text-red-500 ml-auto">
                      <Flag className="w-3.5 h-3.5" /> Report
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      {showReportModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#141414] border border-gray-800 rounded-xl max-w-md w-full p-6 space-y-4">
            <h3 className="text-lg font-bold text-[#E50914]">Community Rules & Reporting</h3>
            <div className="bg-[#1A1A1A] p-3 rounded-md text-xs text-gray-300 space-y-2 border border-gray-800">
              <p>• No harassment, personal attacks, or hate speech.</p>
              <p>• No spamming or self-promotional links.</p>
              <p>• False reporting will result in temporary account restrictions.</p>
            </div>
            
            <label className="flex items-center space-x-2 text-xs text-gray-400 cursor-pointer">
              <input 
                type="checkbox" 
                checked={agreedToRules} 
                onChange={(e) => setAgreedToRules(e.target.checked)}
                className="accent-[#E50914]" 
              />
              <span>I have read and agree to follow the Community Rules.</span>
            </label>

            <div className="flex justify-end space-x-3 pt-2">
              <button 
                onClick={() => setShowReportModal(false)}
                className="px-4 py-2 text-xs rounded-lg border border-gray-800 text-gray-400 hover:bg-gray-800"
              >
                Cancel
              </button>
              <button 
                disabled={!agreedToRules}
                onClick={() => { setShowReportModal(false); alert("Report submitted."); }}
                className="px-4 py-2 text-xs rounded-lg bg-[#E50914] text-white font-semibold disabled:opacity-40"
              >
                Submit Report
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
