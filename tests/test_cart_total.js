// This script tests the cart total calculation issue
async function testCartTotal() {
    const backendUrl = 'http://localhost:8000';
    const token = localStorage.getItem('token');
    
    if (!token) {
        console.error('No token found in localStorage. Please log in first.');
        return;
    }
    
    try {
        console.log('Fetching cart data...');
        const res = await fetch(`${backendUrl}/cart/`, { 
            headers: { 'Authorization': `Bearer ${token}` } 
        });
        
        if (!res.ok) {
            const error = await res.json();
            console.error('Failed to fetch cart:', error);
            return;
        }
        
        const cartData = await res.json();
        console.log('Full cart response:', JSON.stringify(cartData, null, 2));
        
        // Calculate the total manually
        let calculatedTotal = 0;
        if (cartData.items && cartData.items.length > 0) {
            calculatedTotal = cartData.items.reduce((sum, item) => {
                const price = item.price_at_time_of_order || (item.menu_item ? item.menu_item.price : 0);
                return sum + (price * item.quantity);
            }, 0);
        }
        
        console.log('Server total_price:', cartData.total_price);
        console.log('Calculated total:', calculatedTotal);
        
        if (cartData.total_price !== calculatedTotal) {
            console.warn('Total price mismatch detected!');
        }
    } catch (error) {
        console.error('Error testing cart total:', error);
    }
}

testCartTotal();