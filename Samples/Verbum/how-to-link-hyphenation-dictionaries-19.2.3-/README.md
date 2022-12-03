<!-- default badges list -->
![](https://img.shields.io/endpoint?url=https://codecentral.devexpress.com/api/v1/VersionRange/203134499/19.2.3%2B)
[![](https://img.shields.io/badge/Open_in_DevExpress_Support_Center-FF7200?style=flat-square&logo=DevExpress&logoColor=white)](https://supportcenter.devexpress.com/ticket/details/T828525)
[![](https://img.shields.io/badge/📖_How_to_use_DevExpress_Examples-e9f6fc?style=flat-square)](https://docs.devexpress.com/GeneralInformation/403183)
<!-- default badges end -->
# How to Link Hyphenation Dictionaries

The following code sample shows how to enable the word hyphenation in the Rich Text Editor. To accomplish the task, you must first add a hyphenation dictionary to the 
[RichEditControl.HyphenationDictionaries][3] collection.

Once you link hyphenation dictionaries, you can enable or suppress automatic hyphenation in code or within the UI.
[Refer to the Hyphenation topic for more information](https://docs.devexpress.com/WindowsForms/401190/controls-and-libraries/rich-text-editor/hyphenation?).

Please note that DevExpress does not offer hyphenation dictionaries. In this example, we utilize an American hyphenation dictionary from this site: [LibreOffice.org - English Dictionaries][1]. You can download the dictionary source (including the license agreement) from [this link][2]. If you wish to use this dictionary in your application, please ensure the relevant license agreement permits it.


[1]: https://extensions.libreoffice.org/en/extensions/show/english-dictionaries
[2]: https://extensions.libreoffice.org/assets/downloads/41/dict-en-20210101.oxt
[3]: https://docs.devexpress.com/WindowsForms/DevExpress.XtraRichEdit.RichEditControl.HyphenationDictionaries
