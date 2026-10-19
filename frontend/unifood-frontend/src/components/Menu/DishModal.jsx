import React, { useState } from 'react';
import './DishModal.scss';

const DishModal = ({ dish, onClose, onAddToCart }) => {
    const [quantity, setQuantity] = useState(1);

    if (!dish) return null;

    const handleIncrement = () => setQuantity(prev => prev + 1);
    const handleDecrement = () => {
        if (quantity > 1) setQuantity(prev => prev - 1);
    };

    const handleAddClick = () => {
        onAddToCart(dish, quantity);
        onClose();
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <button className="modal-close" onClick={onClose}>&times;</button>
                
                <div className="modal-body">
                    <div className="modal-image">
                        <img 
                            src={dish.image_url || 'https://via.placeholder.com/300x200?text=No+Image'} 
                            alt={dish.food_name} 
                        />
                    </div>
                    
                    <div className="modal-info">
                        <h2>{dish.food_name}</h2>
                        <p className="category">{dish.category}</p>
                        <p className="description">
                            {dish.description || 'Вкусное блюдо из нашего университетского кафе. Попробуйте прямо сейчас!'}
                        </p>
                        
                        {dish.calories && (
                            <span className="calories">{dish.calories} ккал</span>
                        )}

                        <div className="modal-footer">
                            <div className="quantity-controls">
                                <button onClick={handleDecrement} disabled={quantity <= 1}>-</button>
                                <span>{quantity}</span>
                                <button onClick={handleIncrement}>+</button>
                            </div>
                            
                            <button className="add-button" onClick={handleAddClick}>
                                Добавить за {dish.price * quantity} ₽
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DishModal;