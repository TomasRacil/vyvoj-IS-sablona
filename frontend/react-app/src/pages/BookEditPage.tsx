import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import axiosInstance from '../api/axiosInstance';

interface BookUpdateData {
    title: string;
    published_year: number | null;
    isbn: string | null;
}

const BookEditPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [formData, setFormData] = useState<BookUpdateData>({
        title: '',
        published_year: null,
        isbn: null,
    });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchBook = async () => {
            try {
                const response = await axiosInstance.get(`/books/${id}`);
                const { title, published_year, isbn } = response.data;
                setFormData({ title, published_year, isbn });
                setLoading(false);
            } catch (err: any) {
                setError(err.response?.data?.message || 'Chyba při načítání knihy');
                setLoading(false);
            }
        };
        fetchBook();
    }, [id]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSaving(true);
        setError(null);
        try {
            await axiosInstance.put(`/books/${id}`, formData);
            navigate(`/books/${id}`);
        } catch (err: any) {
            setError(err.response?.data?.message || 'Chyba při ukládání změn');
            setSaving(false);
        }
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: name === 'published_year' ? (value ? parseInt(value) : null) : value
        }));
    };

    if (loading) return <div className="text-center p-10 text-gray-500">Načítání knihy pro úpravu...</div>;

    return (
        <div className="max-w-xl mx-auto bg-white p-8 rounded-3xl shadow-2xl border border-gray-100 mt-10">
            <h1 className="text-3xl font-extrabold text-gray-900 mb-8 border-b pb-4">Upravit knihu</h1>
            
            <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                    <label htmlFor="title" className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Název knihy</label>
                    <input
                        id="title"
                        name="title"
                        type="text"
                        required
                        value={formData.title}
                        onChange={handleInputChange}
                        className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 focus:bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all font-medium"
                    />
                </div>

                <div className="grid grid-cols-2 gap-6">
                    <div>
                        <label htmlFor="published_year" className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">Rok vydání</label>
                        <input
                            id="published_year"
                            name="published_year"
                            type="number"
                            value={formData.published_year || ''}
                            onChange={handleInputChange}
                            className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 focus:bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all font-medium"
                        />
                    </div>
                    <div>
                        <label htmlFor="isbn" className="block text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">ISBN</label>
                        <input
                            id="isbn"
                            name="isbn"
                            type="text"
                            value={formData.isbn || ''}
                            onChange={handleInputChange}
                            className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 focus:bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all font-medium"
                        />
                    </div>
                </div>

                {error && <p className="text-red-500 text-sm font-medium">{error}</p>}

                <div className="pt-4 flex space-x-4">
                    <button
                        type="submit"
                        disabled={saving}
                        className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl shadow-lg shadow-blue-200 transition-all disabled:opacity-50"
                    >
                        {saving ? 'Ukládání...' : 'Uložit změny'}
                    </button>
                    <Link
                        to={`/books/${id}`}
                        className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-600 font-bold py-3 rounded-xl text-center transition-all"
                    >
                        Zrušit
                    </Link>
                </div>
            </form>
        </div>
    );
};

export default BookEditPage;
