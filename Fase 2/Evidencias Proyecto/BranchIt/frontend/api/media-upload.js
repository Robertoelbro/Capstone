/* eslint-env node */
import { handleUpload } from "@vercel/blob/client";

export default async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "POST")
    return res.status(405).json({ error: "Método no permitido." });
  try {
    const result = await handleUpload({
      request: req,
      body: req.body,
      onBeforeGenerateToken: async (pathname, payload) => {
        const id = JSON.parse(payload || "{}").id;
        if (!/^[a-f0-9]{32}$/.test(id || "")) throw new Error("Invalid asset");
        const response = await fetch(
          `${process.env.VITE_API_URL}/media/${id}/access?upload=true`,
          {
            headers: { Authorization: req.headers.authorization || "" },
          },
        );
        if (!response.ok) throw new Error("Unauthorized");
        const asset = await response.json();
        if (pathname !== asset.pathname) throw new Error("Invalid path");
        return {
          allowedContentTypes: [asset.mime],
          maximumSizeInBytes: asset.tamano,
          validUntil: Date.now() + 10 * 60 * 1000,
          addRandomSuffix: false,
          allowOverwrite: false,
        };
      },
    });
    return res.status(200).json(result);
  } catch {
    return res
      .status(400)
      .json({
        error:
          "No se pudo autorizar la subida. Revisa tu sesión y vuelve a seleccionar el archivo.",
      });
  }
}
