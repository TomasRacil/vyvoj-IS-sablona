import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import axiosInstance from '../api/axiosInstance';
import { useAuth } from '../contexts/AuthContext';

interface Author {
    id: string;
    first_name: string;
    last_name: string;
}

interface Publisher {
    id: string;
    name: string;
}

interface BookDetail {
    id: string;
    title: string;
    published_year: number | null;
    isbn: string | null;
    publisher: Publisher | null;
    authors: Author[];
}

const BookDetailPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const { userRoles } = useAuth();
    const canEdit = userRoles.includes('admin') || userRoles.includes('editor');
    const [book, setBook] = useState<BookDetail | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchBookDetail = async () => {
            try {
                const response = await axiosInstance.get(`/books/${id}`);
                setBook(response.data);
                setLoading(false);
            } catch (err: any) {
                setError(err.response?.data?.message || 'Kniha nebyla nalezena');
                setLoading(false);
            }
        };

        if (id) fetchBookDetail();
    }, [id]);

    if (loading) return <div className="text-center p-10">Načítání detailu knihy...</div>;
    if (error) return (
        <div className="text-center p-10">
            <p className="text-red-500 mb-4">{error}</p>
            <Link to="/books" className="text-blue-600 hover:underline">Zpět na seznam</Link>
        </div>
    );
    if (!book) return null;

    return (
        <div className="max-w-2xl mx-auto bg-white p-8 rounded-2xl shadow-xl border border-gray-100">
            <div className="flex justify-between items-center mb-6">
                <Link to="/books" className="text-blue-600 hover:underline inline-block">← Zpět na seznam</Link>
                {canEdit && (
                    <Link to={`/books/${id}/edit`} className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-bold shadow-md hover:bg-blue-700 transition-colors">
                        Upravit knihu
                    </Link>
                )}
            </div>
            
            <h1 className="text-4xl font-extrabold mb-6 text-gray-900 border-b pb-4">{book.title}</h1>
            
            <div className="space-y-6">
                <div>
                    <h3 className="text-sm font-uppercase tracking-wider text-gray-500 uppercase">Autoři</h3>
                    <div className="flex flex-wrap gap-2 mt-2">
                        {book.authors.length > 0 ? (
                            book.authors.map(author => (
                                <span key={author.id} className="bg-blue-50 text-blue-700 px-3 py-1 rounded-full font-medium">
                                    {author.first_name} {author.last_name}
                                </span>
                            ))
                        ) : (
                            <span className="text-gray-400">Neznámý autor</span>
                        )}
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-8">
                    <div>
                        <h3 className="text-sm font-uppercase tracking-wider text-gray-500 uppercase">Vydavatel</h3>
                        <p className="mt-1 text-lg font-medium text-gray-800">
                            {book.publisher?.name || 'Neznámý'}
                        </p>
                    </div>
                    <div>
                        <h3 className="text-sm font-uppercase tracking-wider text-gray-500 uppercase">Rok vydání</h3>
                        <p className="mt-1 text-lg font-medium text-gray-800">
                            {book.published_year || 'Neznámý'}
                        </p>
                    </div>
                </div>

                <div>
                    <h3 className="text-sm font-uppercase tracking-wider text-gray-500 uppercase">ISBN</h3>
                    <p className="mt-1 text-lg font-mono text-gray-800">
                        {book.isbn || 'Není k dispozici'}
                    </p>
                </div>
            </div>

            <div className="mt-10 p-4 bg-yellow-50 border border-yellow-100 rounded-xl">
                <p className="text-yellow-800 text-sm italic">
                    <strong>Demo Dynamic Routing:</strong> Tato stránka načítá data pro knihu s ID <code>{id}</code> pomocí dynamické cesty v React Routeru.
                </p>
            </div>
        </div>
    );
};

export default BookDetailPage;
