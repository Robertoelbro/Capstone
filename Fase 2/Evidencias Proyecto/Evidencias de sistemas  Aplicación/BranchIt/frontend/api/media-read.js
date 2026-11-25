/* eslint-env node */
import { issueSignedToken, presignUrl, head } from "@vercel/blob";

export default async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "GET")
    return res.status(405).json({ error: "Método no permitido." });
  const id = req.query.id;
  if (typeof id !== "string" || !/^[a-f0-9]{32}$/.test(id))
    return res.status(400).json({ error: "Archivo inválido." });
  try {
    const response = await fetch(
      `${process.env.VITE_API_URL}/media/${id}/access`,
      {
        headers: { Authorization: req.headers.authorization || "" },
      },
    );
    if (!response.ok)
      return res
        .status(response.status)
        .json({ error: "Archivo no disponible." });
    const asset = await response.json();
    const info = await head(asset.pathname);
    if (info.size > asset.tamano || info.contentType !== asset.mime)
      throw new Error("Invalid file");
    const validUntil = Date.now() + 5 * 60 * 1000;
    const delegation = await issueSignedToken({
      pathname: asset.pathname,
      operations: ["get"],
      validUntil,
    });
    const { presignedUrl } = await presignUrl(delegation, {
      pathname: asset.pathname,
      operation: "get",
      access: "private",
      validUntil,
    });
    return res.status(200).json({ url: presignedUrl });
  } catch {
    return res
      .status(404)
      .json({
        error: "El archivo no está disponible. Intenta subirlo nuevamente.",
      });
  }
}
