import { useNavigate } from 'react-router-dom';
import { NotFound } from '../components';

export default function NotFoundPage() {
  const navigate = useNavigate();

  const handleGoHome = () => {
    navigate('/articles');
  };

  const handleGoBack = () => {
    navigate(-1);
  };

  return <NotFound onGoHome={handleGoHome} onGoBack={handleGoBack} />;
}
