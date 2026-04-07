import { Document, Packer, Paragraph, TextRun } from "docx";
import { PDFDocument, StandardFonts, rgb } from "pdf-lib";

/* ================================================================
   📄 DOCX Generator (Browser-Safe)
================================================================ */
export async function generatePaperDOCX(paperData: any): Promise<Blob> {
  const metaLines = [
    `Organization: ${paperData.organization || "N/A"}`,
    `Program: ${paperData.program || "N/A"}`,
    `Course: ${paperData.course || "N/A"}`,
    `Exam Date: ${paperData.exam_date || "N/A"}`,
    `Subject: ${paperData.subject || "N/A"}`,
    `Total Marks: ${paperData.total_marks || "N/A"}`,
  ];

  const doc = new Document({
    sections: [
      {
        children: [
          new Paragraph({
            children: [new TextRun({ text: "Question Paper", bold: true, size: 32 })],
            spacing: { after: 300 },
          }),

          ...metaLines.map(
            (line) => new Paragraph({ children: [new TextRun({ text: line, size: 24 })] })
          ),

          new Paragraph({ text: "" }),

          new Paragraph({
            children: [new TextRun({ text: "Instructions:", bold: true, size: 26 })],
            spacing: { after: 200 },
          }),

          ...(paperData.instructions || []).map(
            (i: string) =>
              new Paragraph({ children: [new TextRun({ text: `• ${i}`, size: 22 })] })
          ),

          ...(paperData.sections || []).flatMap((section: any, sIdx: number) => [
            new Paragraph({
              children: [
                new TextRun({
                  text: `\nSection ${section.section || String.fromCharCode(65 + sIdx)} - ${
                    section.question_type || ""
                  }`,
                  bold: true,
                  size: 26,
                  underline: {},
                }),
              ],
              spacing: { before: 200, after: 100 },
            }),
            ...(section.questions || []).map(
              (q: any, idx: number) =>
                new Paragraph({
                  children: [
                    new TextRun({
                      text: `${idx + 1}. ${q.text || "Question unavailable"} (${
                        q.marks || 0
                      } marks)`,
                      size: 22,
                    }),
                    new TextRun({
                      text: `\n   [${q.blooms_taxonomy_level || ""}] Topic: ${
                        q.topic || "N/A"
                      }`,
                      italics: true,
                      size: 20,
                    }),
                  ],
                  spacing: { after: 100 },
                })
            ),
          ]),
        ],
      },
    ],
  });

  // ✅ Use browser-safe version
  const blob = await Packer.toBlob(doc);
  return blob;
}

/* ================================================================
   🧾 PDF Generator (Browser-Safe)
================================================================ */

/**
 * 🎨 Improved, Center-Aligned PDF Generator
 */

export async function generatePaperPDF(paperData: any): Promise<Blob> {
  const pdfDoc = await PDFDocument.create();
  const page = pdfDoc.addPage([595.28, 841.89]); // A4
  const { width, height } = page.getSize();

  const font = await pdfDoc.embedFont(StandardFonts.Helvetica);
  const fontBold = await pdfDoc.embedFont(StandardFonts.HelveticaBold);

  // Margins
  const marginLeft = 60;
  const marginRight = 60;
  const maxWidth = width - marginLeft - marginRight;

  let y = height - 60; // start from top margin
  const fontSizeTitle = 18;
  const fontSizeSub = 13;
  const fontSizeText = 12;

  // 🧩 Utility: wrap text to fit page width
  const wrapText = (text: string, fontUsed: any, fontSize: number): string[] => {
    const words = text.split(" ");
    const lines: string[] = [];
    let line = "";

    words.forEach((word) => {
      const testLine = line ? `${line} ${word}` : word;
      const testWidth = fontUsed.widthOfTextAtSize(testLine, fontSize);

      if (testWidth > maxWidth) {
        lines.push(line);
        line = word;
      } else {
        line = testLine;
      }
    });
    if (line) lines.push(line);
    return lines;
  };

  // 🎯 Draw centered text (title/header)
  const centerText = (
    text: string,
    { bold = false, size = 12, spacing = 18 }: { bold?: boolean; size?: number; spacing?: number } = {}
  ) => {
    const usedFont = bold ? fontBold : font;
    const textWidth = usedFont.widthOfTextAtSize(text, size);
    const x = (width - textWidth) / 2;
    page.drawText(text, { x, y, size, font: usedFont, color: rgb(0, 0, 0) });
    y -= spacing;
  };

  // 🎯 Draw left-aligned wrapped text
  const leftText = (
    text: string,
    { bold = false, size = 12, moveY = 16 }: { bold?: boolean; size?: number; moveY?: number } = {}
  ) => {
    const usedFont = bold ? fontBold : font;
    const lines = wrapText(text, usedFont, size);
    lines.forEach((line) => {
      y -= moveY;
      page.drawText(line, { x: marginLeft, y, size, font: usedFont, color: rgb(0, 0, 0) });
    });
  };

  /* ===========================
     🏛 Header Section
  =========================== */
  centerText(paperData.organization || "University Examination", { bold: true, size: 16, spacing: 20 });
  centerText(paperData.exam_name || "End Semester Examination", { bold: true, size: fontSizeTitle, spacing: 22 });

  const courseProgram = `${paperData.course || ""}${paperData.program ? " - " + paperData.program : ""}`;
  const instDate = `${paperData.organization || ""}${paperData.exam_date ? "   |   " + paperData.exam_date : ""}`;

  if (courseProgram.trim()) centerText(courseProgram, { size: fontSizeSub, spacing: 18 });
  if (instDate.trim()) centerText(instDate, { size: fontSizeSub, spacing: 18 });

  centerText(`Subject: ${paperData.subject || ""}`, { bold: true, size: 14, spacing: 20 });
  centerText(`Total Marks: ${paperData.total_marks || ""}`, { size: 12, spacing: 30 });

  /* ===========================
     🧾 Instructions
  =========================== */
  leftText("Instructions:", { bold: true, size: 13, moveY: 24 });
  (paperData.instructions || []).forEach((inst: string) => leftText(`• ${inst}`, { moveY: 14 }));

  y -= 10;

  /* ===========================
     🧩 Sections
  =========================== */
  (paperData.sections || []).forEach((section: any, sIdx: number) => {
    leftText(
      `Section ${section.section || String.fromCharCode(65 + sIdx)} - ${section.question_type || ""}`,
      { bold: true, size: 13, moveY: 30 }
    );

    (section.questions || []).forEach((q: any, qIdx: number) => {
      leftText(`${qIdx + 1}. ${q.text || "Question unavailable"} (${q.marks || 0} marks)`, {
        moveY: 18,
      });
      leftText(`   [${q.blooms_taxonomy_level || ""}] Topic: ${q.topic || ""}`, {
        moveY: 14,
      });
    });

    y -= 10;
  });

  /* ===========================
     🪄 Export
  =========================== */
  const base64Data = await pdfDoc.saveAsBase64({ dataUri: false });
  const byteArray = Uint8Array.from(atob(base64Data), (c) => c.charCodeAt(0));

  return new Blob([byteArray], { type: "application/pdf" });
}
