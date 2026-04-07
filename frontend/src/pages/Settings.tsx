import { useEffect, useState } from "react";
import { User, Building, Save, Phone, Briefcase, Layers } from "lucide-react";
import { useAuth } from "../contexts/AuthContext";
import { supabase } from "../lib/supabase"; // Ensure Supabase is initialized

export default function Settings() {
  const { user } = useAuth();
  const [profile, setProfile] = useState({
    full_name: "",
    organization_name: "",
    mobile_number: "",
    designation: "",
    department: "",
    role: "teacher",
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Fetch user profile data
  useEffect(() => {
    const fetchProfile = async () => {
      if (!user) return;

      const { data, error } = await supabase
        .from("profiles")
        .select("*")
        .eq("id", user.id)
        .single();

      if (error) {
        console.error("Error loading profile:", error);
      } else if (data) {
        setProfile({
          full_name: data.full_name || "",
          organization_name: data.organization_name || "",
          mobile_number: data.mobile_number || "",
          designation: data.designation || "",
          department: data.department || "",
          role: data.role || "teacher",
        });
      }
      setLoading(false);
    };

    fetchProfile();
  }, [user]);

  // Save updated profile
  const handleSave = async () => {
    if (!user) return;
    setSaving(true);

    const updates = {
      id: user.id,
      full_name: profile.full_name,
      organization_name: profile.organization_name || null,
      mobile_number: profile.mobile_number,
      designation: profile.designation,
      department: profile.department,
      role: profile.role,
      updated_at: new Date(),
    };

    const { error } = await supabase.from("profiles").upsert(updates);

    setSaving(false);
    if (error) {
      console.error("Error saving profile:", error);
      alert("Failed to save settings.");
    } else {
      alert("Settings saved successfully!");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen text-slate-500">
        Loading profile...
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-auto bg-slate-50">
      <div className="max-w-4xl mx-auto p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900 mb-2">Settings</h1>
          <p className="text-slate-600">Manage your account and preferences</p>
        </div>

        <div className="space-y-6">
          {/* Profile Information */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-xl font-semibold text-slate-900 mb-6">
              Profile Information
            </h2>

            <div className="space-y-4">
              {/* Email */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={user?.email || ""}
                  disabled
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg bg-slate-50 text-slate-500"
                />
                <p className="text-xs text-slate-500 mt-1">
                  Email cannot be changed
                </p>
              </div>

              {/* Full Name */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Full Name
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    type="text"
                    value={profile.full_name}
                    onChange={(e) =>
                      setProfile({ ...profile, full_name: e.target.value })
                    }
                    placeholder="Enter your full name"
                    className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-transparent outline-none"
                  />
                </div>
              </div>

              {/* Organization Name */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Organization Name
                </label>
                <div className="relative">
                  <Building className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    type="text"
                    value={profile.organization_name}
                    onChange={(e) =>
                      setProfile({
                        ...profile,
                        organization_name: e.target.value,
                      })
                    }
                    placeholder="Enter your organization name"
                    className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-transparent outline-none"
                  />
                </div>
              </div>

              {/* Mobile Number */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Mobile Number
                </label>
                <div className="relative">
                  <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    type="text"
                    value={profile.mobile_number}
                    onChange={(e) =>
                      setProfile({ ...profile, mobile_number: e.target.value })
                    }
                    placeholder="Enter your phone number"
                    className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-transparent outline-none"
                  />
                </div>
              </div>

              {/* Designation */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Designation
                </label>
                <div className="relative">
                  <Briefcase className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    type="text"
                    value={profile.designation}
                    onChange={(e) =>
                      setProfile({ ...profile, designation: e.target.value })
                    }
                    placeholder="Enter your designation"
                    className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-transparent outline-none"
                  />
                </div>
              </div>

              {/* Department */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Department
                </label>
                <div className="relative">
                  <Layers className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    type="text"
                    value={profile.department}
                    onChange={(e) =>
                      setProfile({ ...profile, department: e.target.value })
                    }
                    placeholder="Enter your department"
                    className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-transparent outline-none"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Save Button */}
          <button
            onClick={handleSave}
            disabled={saving}
            className="w-full py-3 bg-slate-800 text-white rounded-lg hover:bg-slate-700 transition-colors font-medium flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            <Save className="w-5 h-5" />
            <span>{saving ? "Saving..." : "Save Changes"}</span>
          </button>
        </div>
      </div>
    </div>
  );
}
