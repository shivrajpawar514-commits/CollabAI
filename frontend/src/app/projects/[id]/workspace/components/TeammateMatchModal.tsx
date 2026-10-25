"use client";

import { useEffect, useState } from "react";
import { Users, X, Check, Sparkles, AlertCircle, Clock, CheckCircle2, UserPlus } from "lucide-react";
import { api, CandidateMatch } from "@/lib/api";

interface TeammateMatchModalProps {
  projectId: string;
  projectTitle: string;
  onClose: () => void;
  onInvited: () => void;
}

export default function TeammateMatchModal({
  projectId,
  projectTitle,
  onClose,
  onInvited,
}: TeammateMatchModalProps) {
  const [candidates, setCandidates] = useState<CandidateMatch[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [invitedMap, setInvitedMap] = useState<Record<string, boolean>>({});
  const [invitingId, setInvitingId] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    api
      .recommendTeammates(projectId)
      .then((res) => {
        if (mounted) {
          setCandidates(res.recommendations);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (mounted) {
          setError(err.message || "Failed to load candidate recommendations");
          setLoading(false);
        }
      });
    return () => {
      mounted = false;
    };
  }, [projectId]);

  const handleInvite = async (candidate: CandidateMatch) => {
    setInvitingId(candidate.user_id);
    try {
      const role = candidate.preferred_roles?.[0] || "Software Engineer";
      await api.inviteMember(projectId, {
        recipient_id: candidate.user_id,
        role_name: role,
        message: `Matched via AI Teammate Recommender (${candidate.match_score}% fit)`,
      });
      setInvitedMap((prev) => ({ ...prev, [candidate.user_id]: true }));

      onInvited();
    } catch (err: any) {
      alert(err.message || "Failed to send invitation");
    } finally {
      setInvitingId(null);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-3xl glass-panel rounded-2xl border border-indigo-500/30 p-6 space-y-5 bg-[#0b0e1b] shadow-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between pb-3 border-b border-white/10">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-cyan-400 flex items-center justify-center border border-indigo-500/30">
              <Users className="w-4 h-4" />
            </div>
            <div>
              <h2 className="font-bold text-white text-sm sm:text-base flex items-center gap-2">
                AI Teammate Recommendations
                <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              </h2>
              <p className="text-[11px] text-slate-400 line-clamp-1">
                Scored by Complementary Skills (35%), Domain Interest (20%), and Availability
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/10"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {loading && (
          <div className="py-16 flex flex-col items-center justify-center gap-3">
            <div className="w-8 h-8 border-2 border-indigo-500 border-t-cyan-400 rounded-full animate-spin" />
            <p className="text-xs text-slate-300 font-medium">
              Scanning active students and computing multi-factor compatibility scores...
            </p>
          </div>
        )}

        {error && (
          <div className="p-3.5 rounded-xl bg-red-500/15 border border-red-500/30 text-red-200 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {!loading && candidates.length === 0 && !error && (
          <div className="py-12 text-center text-slate-400 text-xs">
            No outside candidates found. All available students may already be on the team!
          </div>
        )}

        {!loading && candidates.length > 0 && (
          <div className="space-y-3">
            {candidates.map((cand) => {
              const isInvited = invitedMap[cand.user_id];
              const isProcessing = invitingId === cand.user_id;

              const scoreBadgeColor =
                cand.match_score >= 80
                  ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                  : cand.match_score >= 60
                  ? "bg-cyan-500/20 text-cyan-300 border-cyan-500/40"
                  : "bg-indigo-500/20 text-indigo-300 border-indigo-500/40";

              return (
                <div
                  key={cand.user_id}
                  className="p-4 rounded-xl bg-white/[0.02] border border-white/5 hover:border-indigo-500/30 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4 text-xs"
                >
                  <div className="space-y-2 flex-1">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-indigo-500 to-cyan-500 text-white font-bold text-xs flex items-center justify-center shrink-0">
                        {cand.avatar_url ? (
                          <img src={cand.avatar_url} alt={cand.name} className="w-full h-full rounded-full object-cover" />
                        ) : (
                          cand.name.charAt(0)
                        )}
                      </div>

                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-white text-sm">{cand.name}</span>
                          <span className={`text-[10px] font-extrabold px-2 py-0.5 rounded-md border ${scoreBadgeColor}`}>
                            {cand.match_score}% Match
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400">
                          {cand.college ? `${cand.college} • ` : ""}{cand.year || "Student"}
                        </p>
                      </div>
                    </div>

                    <p className="text-[11px] text-slate-300 leading-relaxed italic">
                      "{cand.explanation}"
                    </p>

                    {/* Matching skills tags */}
                    <div className="flex flex-wrap items-center gap-1.5 pt-1">
                      <span className="text-[10px] text-slate-500 font-semibold uppercase">Matching:</span>
                      {cand.matching_skills.map((sk, i) => (
                        <span key={i} className="px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-300 text-[10px] font-medium flex items-center gap-1">
                          <Check className="w-2.5 h-2.5 text-emerald-400" /> {sk}
                        </span>
                      ))}

                      {cand.availability_hours && (
                        <span className="px-2 py-0.5 rounded bg-white/5 text-slate-300 text-[10px] flex items-center gap-1 ml-auto">
                          <Clock className="w-2.5 h-2.5 text-cyan-400" />
                          {cand.availability_hours}h/week
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="sm:text-right shrink-0">
                    <button
                      type="button"
                      disabled={isInvited || isProcessing}
                      onClick={() => handleInvite(cand)}
                      className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all ${
                        isInvited
                          ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 cursor-default"
                          : "bg-indigo-600 hover:bg-indigo-500 text-white shadow-md shadow-indigo-600/30"
                      }`}
                    >
                      {isInvited ? (
                        <>
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                          Invitation Sent
                        </>
                      ) : isProcessing ? (
                        <>
                          <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                          Inviting...
                        </>
                      ) : (
                        <>
                          <UserPlus className="w-3.5 h-3.5 text-cyan-300" />
                          Invite to Team
                        </>
                      )}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
