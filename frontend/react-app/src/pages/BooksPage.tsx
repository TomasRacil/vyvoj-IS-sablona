import React, { useEffect, useState } from 'react';
import axiosInstance from '../api/axiosInstance';
import { Link } from 'react-router-dom';

interface Book {
    id: string;
    title: string;
    published_year: number | null;
    isbn: string | null;
}

const BooksPage: React.FC = () => {
    const [books, setBooks] = useState<Book[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchBooks = async () => {
            try {
                const response = await axiosInstance.get('/books/');
                setBooks(response.data);
                setLoading(false);
            } catch (err: any) {
                setError(err.response?.data?.message || 'Chyba při načítání knih');
                setLoading(false);
            }
        };

        fetchBooks();
    }, []);

    if (loading) return <div className="text-center p-10">Načítání...</div>;
    if (error) return <div className="text-red-500 p-10">{error}</div>;

    return (
        <div className="max-w-4xl mx-auto">
            <h1 className="text-3xl font-bold mb-8 text-gray-800">Seznam knih</h1>
            <div className="grid gap-6 md:grid-cols-2">
                {books.map((book) => (
                    <div key={book.id} className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow border border-gray-100">
                        <h2 className="text-xl font-semibold mb-2 text-blue-700">{book.title}</h2>
                        <p className="text-gray-600 mb-4">
                            Rok vydání: {book.published_year || 'Neznámý'}<br />
                            ISBN: {book.isbn || 'Není k dispozici'}
                        </p>
                        <Link 
                            to={`/books/${book.id}`} 
                            className="inline-block bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                        >
                            Detail knihy
                        </Link>
                    </div>
                ))}
            </div>
            {books.length === 0 && <p className="text-gray-500">Žádné knihy nebyly nalezeny.</p>}
        </div>
    );
};

export default BooksPage;
