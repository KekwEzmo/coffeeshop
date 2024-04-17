import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

function NotFoundPage() {
  const navigate = useNavigate();

  useEffect(() => {
    navigate("/404", { replace: true });
  }, []);

  return (
    <div className="mainsection">
      <h1>404 - Page Not Found</h1>
      <p>The page you are looking for does not exist. Sadge.</p>
    </div>
  );
}

export default NotFoundPage;
