export const ENVIRONMENTS = {
  default: {
    key: "kargil",
    label: "Kargil",
    region: "Ladakh · Winter passage",
    headline: "Where the mountains hold their breath.",
    subline: "Find your way through a world of snow and sky.",
    terrain: "mountain",
    weather: "Cold mountain wind",
    temperature: "−8°",
    image: "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=2400&q=90",
  },
  mysuru: {
    key: "mysuru",
    label: "Mysuru",
    region: "India · Heritage season",
    headline: "Make room for wonder.",
    subline: "A thoughtful plan leaves space to wander.",
    terrain: "palace",
    weather: "Clear and warm",
    temperature: "27°",
    image: "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?auto=format&fit=crop&w=2400&q=85",
  },
  kochi: {
    key: "kochi",
    label: "Kochi",
    region: "India · Coastal morning",
    headline: "Follow the light to the coast.",
    subline: "Let the next horizon shape the route.",
    terrain: "coast",
    weather: "Sea breeze",
    temperature: "29°",
    image: "https://images.unsplash.com/photo-1593693397690-362cb9666fc2?auto=format&fit=crop&w=2400&q=85",
  },
  goa: {
    key: "goa",
    label: "Goa",
    region: "India · Golden hour",
    headline: "Leave a little room for the unexpected.",
    subline: "The best itineraries breathe.",
    terrain: "coast",
    weather: "Warm and bright",
    temperature: "30°",
    image: "https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=2400&q=85",
  },
};

export function getEnvironment(destination) {
  if (!destination) return ENVIRONMENTS.default;
  const city = destination.city?.toLowerCase();
  return ENVIRONMENTS[city] || {
    ...ENVIRONMENTS.default,
    label: destination.city,
    region: `${destination.country} · RoamGenie`,
    image: ENVIRONMENTS.default.image,
  };
}