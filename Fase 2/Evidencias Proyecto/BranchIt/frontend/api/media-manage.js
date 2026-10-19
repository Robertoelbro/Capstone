/* eslint-env node */
import { get, head, del } from "@vercel/blob";
import { fileTypeFromBuffer } from "file-type";
import { parseBuffer } from "music-metadata";

export default async function handler(req, res) {
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "POST" && req.method !== "DELETE")
    return res.status(405).json({ error: "Método no permitido." });
  const id = req.body?.id;
  if (!/^[a-f0-9]{32}$/.test(id || ""))
    return res.status(400).json({ error: "Archivo inválido." });
  const headers = {
    Authorization: req.headers.authorization || "",
    "X-Media-Service": process.env.MEDIA_SERVICE_SECRET || "",
  };
  const base = `${process.env.VITE_API_URL}/media/${id}`;
  try {
    const response = await fetch(
      `${base}/access?${
        req.method === "DELETE" ? "remove=true" : "upload=true"
      }`,
      { headers },
    );
    if (!response.ok) {
      const body = await response.json();
      return res
        .status(response.status)
        .json({ error: body.detail || "Sin acceso al archivo." });
    }
    const asset = await response.json();
    if (req.method === "DELETE") {
      await del(asset.pathname);
      const removed = await fetch(base, { method: "DELETE", headers });
      if (!removed.ok)
        return res
          .status(409)
          .json({
            error: "No se pudo liberar el registro. Intenta nuevamente.",
          });
      return res.status(200).json({ ok: true });
    }
    const info = await head(asset.pathname);
    if (info.size !== asset.tamano || info.contentType !== asset.mime)
      return res
        .status(422)
        .json({
          error: "El archivo no coincide con el formato o tamaño declarado.",
        });
    const object = await get(asset.pathname, { access: "private" });
    if (!object || object.statusCode !== 200) throw new Error("Missing file");
    const bytes = Buffer.from(await new Response(object.stream).arrayBuffer());
    const detected = await fileTypeFromBuffer(bytes);
    if (detected?.mime !== asset.mime)
      return res
        .status(422)
        .json({
          error: "El contenido del archivo no corresponde a su formato.",
        });
    if (asset.tipo === "presentacion" || asset.tipo === "proyecto") {
      const metadata = await parseBuffer(
        bytes,
        { mimeType: asset.mime, size: bytes.length },
        { duration: true },
      );
      const seconds = metadata.format.duration;
      const max = asset.tipo === "presentacion" ? 60 : 180;
      if (!Number.isFinite(seconds) || seconds <= 0 || seconds > max)
        return res
          .status(422)
          .json({
            error: `El video debe tener una duración verificable de hasta ${max} segundos.`,
          });
    }
    const saved = await fetch(`${base}/verified`, { method: "POST", headers });
    if (!saved.ok) throw new Error("Verification failed");
    return res.status(200).json({ ok: true });
  } catch {
    return res
      .status(503)
      .json({
        error:
          "No pudimos verificar el archivo. Reintenta o utiliza un enlace.",
      });
  }
}
