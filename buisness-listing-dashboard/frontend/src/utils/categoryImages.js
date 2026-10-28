// src/utils/categoryImages.js

export const CATEGORY_IMAGES = {
  Restaurant: 'https://images.unsplash.com/photo-1544025162-d76694265947?w=600&auto=format&fit=crop&q=80',
  Cafe: 'https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=600&auto=format&fit=crop&q=80',
  Hotel: 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600&auto=format&fit=crop&q=80',
  'Retail Store': 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=600&auto=format&fit=crop&q=80',
  Grocery: 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=600&auto=format&fit=crop&q=80',
  Pharmacy: 'https://images.unsplash.com/photo-1587854692152-cbe660dbde88?w=600&auto=format&fit=crop&q=80',
  Hospital: 'https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=600&auto=format&fit=crop&q=80',
  Clinic: 'https://images.unsplash.com/photo-1629909613654-28e377c37b09?w=600&auto=format&fit=crop&q=80',
  School: 'https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=600&auto=format&fit=crop&q=80',
  College: 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=600&auto=format&fit=crop&q=80',
  Bank: 'https://images.unsplash.com/photo-1541354329998-f4d9a9f9297f?w=600&auto=format&fit=crop&q=80',
  ATM: 'https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=600&auto=format&fit=crop&q=80',
  Salon: 'https://images.unsplash.com/photo-1560066984-138dadb4c035?w=600&auto=format&fit=crop&q=80',
  Spa: 'https://images.unsplash.com/photo-1540555700478-4be289fbecef?w=600&auto=format&fit=crop&q=80',
  Gym: 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=600&auto=format&fit=crop&q=80',
  Bakery: 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=600&auto=format&fit=crop&q=80',
  Electronics: 'https://images.unsplash.com/photo-1550009158-9ebf69173e03?w=600&auto=format&fit=crop&q=80',
  Clothing: 'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=600&auto=format&fit=crop&q=80',
  Furniture: 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&auto=format&fit=crop&q=80',
  'Real Estate': 'https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=600&auto=format&fit=crop&q=80',
  Automobile: 'https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=600&auto=format&fit=crop&q=80',
  'Petrol Station': 'https://images.unsplash.com/photo-1545454675-3531b543be5d?w=600&auto=format&fit=crop&q=80',
  Hardware: 'https://images.unsplash.com/photo-1581244277943-fe4a9c777189?w=600&auto=format&fit=crop&q=80',
  Bookstore: 'https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=600&auto=format&fit=crop&q=80',
  Jewellery: 'https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=600&auto=format&fit=crop&q=80',
};

const FALLBACK_IMAGES = [
  'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=600&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1498654896293-37aacf113fd9?w=600&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=600&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1552566626-52f8b828add9?w=600&auto=format&fit=crop&q=80',
];

export function getListingImage(category, id = 0) {
  if (category && CATEGORY_IMAGES[category]) {
    return CATEGORY_IMAGES[category];
  }
  const idx = Math.abs(Number(id) || 0) % FALLBACK_IMAGES.length;
  return FALLBACK_IMAGES[idx];
}

// Generate consistent fake price for the card footer
export function getListingPrice(id = 0) {
  const prices = ['$25', '$32', '$18', '$45', '$22', '$28', '$50', '$35', '$15'];
  return prices[Math.abs(Number(id) || 0) % prices.length];
}

// Generate realistic mock rating
export function getListingRating(id = 0) {
  const ratings = ['(1)', '(2)', '(0)', '(3)', '(1)', '(4)'];
  return ratings[Math.abs(Number(id) || 0) % ratings.length];
}
