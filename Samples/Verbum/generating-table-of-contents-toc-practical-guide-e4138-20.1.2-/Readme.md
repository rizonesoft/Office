<!-- default badges list -->
![](https://img.shields.io/endpoint?url=https://codecentral.devexpress.com/api/v1/VersionRange/128609258/20.1.2%2B)
[![](https://img.shields.io/badge/Open_in_DevExpress_Support_Center-FF7200?style=flat-square&logo=DevExpress&logoColor=white)](https://supportcenter.devexpress.com/ticket/details/E4138)
[![](https://img.shields.io/badge/📖_How_to_use_DevExpress_Examples-e9f6fc?style=flat-square)](https://docs.devexpress.com/GeneralInformation/403183)
<!-- default badges end -->
<!-- default file list -->
*Files to look at*:

* [Form1.cs](./CS/Form1.cs) (VB: [Form1.vb](./VB/Form1.vb))
* [Program.cs](./CS/Program.cs) (VB: [Program.vb](./VB/Program.vb))
<!-- default file list end -->
# Generating Table Of Contents (TOC): Practical Guide


<p>This example illustrates the simplest approaches to generate a TOC for a given source document.</p><p>Lets imagine that you have obtained a document and you need to generate a TOC for this document. Here are the steps you need to execute for this purpose:</p><p>1) Decide which parts for the document should be TOC entries.<br />
This step is specific to your document. For instance, this document might contain several headings in the following form: <strong>"Chapter NoXY"</strong>. Generally, you can use Search API (see the <a href="https://www.devexpress.com/Support/Center/p/E1677">Using the Search and Replace API functionality</a> and <a href="https://www.devexpress.com/Support/Center/p/E3147">Search API - An example of use</a> examples) to find the position of these parts in the document. In this particular example, we search for TOC entries (see the <strong>SearchForTOCEntries()</strong> method) by examining the font size of the paragraphs. This approach is based on the <a href="https://www.devexpress.com/Support/Center/p/E4011">How to list fonts that are used in a document</a> code example.</p><p>2) Mark TOC entries in a special manner.<br />
This step is required because the <a href="http://documentation.devexpress.com/#WindowsForms/CustomDocument9718"><u>TOC</u></a> field, which will be added in the next step, should be able to recognize document parts as a TOC entries when this field is updated (see <a href="http://documentation.devexpress.com/#WindowsForms/CustomDocument11166"><u>Fields</u></a> to learn more). We can use the following simple approaches:</p><p>- Paragraph styles with set outline levels<br />
You need to create and apply <a href="http://documentation.devexpress.com/#CoreLibraries/clsDevExpressXtraRichEditAPINativeParagraphStyletopic"><u>ParagraphStyles</u></a> with specific <a href="http://documentation.devexpress.com/#CoreLibraries/DevExpressXtraRichEditAPINativeParagraphPropertiesBase_OutlineLeveltopic"><u>ParagraphPropertiesBase.OutlineLevel Property</u></a> values. Take a moment to look at the <a href="https://www.devexpress.com/Support/Center/p/E2670">How to create and apply document styles</a> code example to learn more about Styles API.</p><p>- Outline levels<br />
Simply apply specific outline levels to paragraphs considered TOC entries</p><p>- <a href="http://documentation.devexpress.com/#WindowsForms/CustomDocument9719"><u>TC</u></a> fields<br />
Insert TC fields in the document. We have a code example that illustrates how to insert fields in code: <a href="https://www.devexpress.com/Support/Center/p/E4004">How to create nested fields programmatically</a></p><p>3) Add a TOC field to the document and update this field (see the <strong>InsertTOC()</strong> method).<br />
A TOC field should have switches that correspond to the method in which TOC entries are marked in the previous step.</p><p>Here is a screenshot that illustrates the operation of a sample application:</p><p><img src="https://raw.githubusercontent.com/DevExpress-Examples/generating-table-of-contents-toc-practical-guide-e4138/13.1.4+/media/749fff65-90c8-431f-96aa-418ff8788b8d.png"></p><p>Take a moment to look at the <a href="http://community.devexpress.com/blogs/rachelreese/archive/2011/08/25/rich-text-editor-table-of-contents.aspx"><u>Rachel Reese - DevExpress Scheduler & RichEdit Blog</u></a> and related webinar to learn the basics of the TOC feature.</p>

<br/>


