import React, { useState, useEffect } from 'react';
import axios from 'axios';
import DishModal from './DishModal';
import './MenuList.scss';

const MenuList = () => {
    const [dishes, setDishes] = useState([]);
    const [selectedDish, setSelectedDish] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchMenu = async () => {
            try {
                const response = await axios.get('http://localhost:8001/menu/');
                setDishes(response.data);
            } catch (error) {
                console.error("Ошибка загрузки меню:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchMenu();
    }, []);

    const handleAddToCart = async (dish, quantity) => {
        try {
            const token = localStorage.getItem('token');
            await axios.post(
                'http://localhost:8001/cart/',
                { menu_item_id: dish.id, quantity: quantity },
                { headers: { Authorization: `Bearer ${token}` } }
            );
            alert(`${dish.food_name} добавлен в корзину!`);
        } catch (error) {
            console.error("Ошибка добавления в корзину:", error);
            alert("Нужно войти в систему");
        }
    };

    if (loading) return <div className="loader">Загрузка меню...</div>;

    return (
        <div className="menu-container">
            <h1>Меню UniFood</h1>
            <div className="menu-grid">
                {dishes.map(dish => (
                    <div 
                        key={dish.id} 
                        className="dish-card" 
                        onClick={() => setSelectedDish(dish)}
                    >
                        <img src={dish.image_url || 'https://via.placeholder.com/150'} alt={dish.food_name} />
                        <div className="dish-card-info">
                            <h3>{dish.food_name}</h3>
                            <p>{dish.price} ₽</p>
                        </div>
                    </div>
                ))}
            </div>

            {selectedDish && (
                <DishModal 
                    dish={selectedDish} 
                    onClose={() => setSelectedDish(null)} 
                    onAddToCart={handleAddToCart}
                />
            )}
        </div>
    );
};

export default MenuList;