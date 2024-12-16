import React from 'react';

const ProductCard = ({name, image, onClick}) => {
    return (
        <div style={styles.cardContainer}>
            <img
                src={`${image}?width=100`}
                alt={name}
                style={styles.image}
                onError={(e) => { e.target.src = "https://via.placeholder.com/150"; }}
            />
            <p style={styles.productName}>{name}</p>
            {onClick && <button
                onClick={onClick}
              >
                Show similar
              </button>}
        </div>
    );
};

const styles = {
    cardContainer: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        border: '1px solid #ddd',
        borderRadius: '8px',
        padding: '8px',
        width: '150px',
        boxShadow: '0 2px 5px rgba(0,0,0,0.2)',
        textAlign: 'center',
        backgroundColor: '#fff',
        margin: '10px',
    },
    image: {
        width: '100px',
        height: '100px',
        objectFit: 'cover',
        borderRadius: '4px',
    },
    productName: {
        fontSize: '14px',
        fontWeight: 'bold',
        marginTop: '8px',
        color: '#333',
    },
};

export default ProductCard;
