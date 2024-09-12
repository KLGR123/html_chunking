###  The most practical HTML chunking

Our HTML chunking algorithm operates through a well-structured process that involves several key stages, each tailored to efficiently chunk and merge HTML content while adhering to a token limit. This approach is highly suitable for scenarios where token limitations are critical, and the need for accurate HTML parsing is paramount, especially in tasks like web automation or navigation where HTML content serves as input.

#### Key Features
- **Token-Aware Splitting**: By leveraging token counts, the algorithm ensures compatibility with models like GPT-3.5-turbo, allowing efficient processing of large HTML documents.
- **Optional Content-Aware Cleaning**: The optional cleaning step minimizes irrelevant content, improving token usage efficiency. This flexibility allows users to adapt the algorithm to their specific use case.
- **DOM Structure Preservation**: The algorithm respects the hierarchical structure of the DOM, ensuring that HTML chunks remain contextually valid and mergeable. Retaining the path structure is particularly beneficial for challenging tasks like web understanding and navigation that require full HTML syntax for accurate parsing.
- **Efficient Greedy Merging**: The greedy merging process combines chunks in a straightforward, sequential manner, optimizing for larger yet manageable segments of HTML while staying within token constraints.

#### Usage

```
from html_chunking import get_html_chunk

html = """
<html darker-dark-theme="" darker-dark-theme-deprecate="" lang="en" style="font-size: 10px;font-family: Roboto, Arial, sans-serif;" system-icons="" typography="" typography-spacing=""><body><ytd-app><ytd-masthead class="shell" id="masthead" logo-type="YOUTUBE_LOGO" slot="masthead"><div class="ytd-searchbox-spt" id="search-container" slot="search-container"></div><div class="ytd-searchbox-spt" id="search-input" slot="search-input"><input autocapitalize="none" autocomplete="off" autocorrect="off" hidden="" id="search" name="search_query" spellcheck="false" tabindex="0" type="text"/></div><svg class="external-icon" id="menu-icon" preserveaspectratio="xMidYMid meet"><g class="yt-icons-ext" id="menu" viewbox="0 0 24 24"><path d="M21,6H3V5h18V6z M21,11H3v1h18V11z M21,17H3v1h18V17z"></path></g></svg><div id="masthead-logo" slot="masthead-logo"><span id="country-code"></span></div><div id="masthead-skeleton-icons" slot="masthead-skeleton"><div class="masthead-skeleton-icon"></div><div class="masthead-skeleton-icon"></div><div class="masthead-skeleton-icon"></div></div></ytd-masthead></ytd-app><link href="https://www.youtube.com/s/desktop/536ed9a8/cssbin/www-main-desktop-watch-page-skeleton.css" name="www-main-desktop-watch-page-skeleton" nonce="2kzKHraEELEaWexSX3PyNg" rel="stylesheet"/></body></html>
"""

merged_chunks = get_html_chunk(html, max_tokens=500, is_clean_html=True, attr_cutoff_len=25)
merged_chunks
```

The `get_html_chunk` function is designed to split and merge HTML content into manageable chunks based on token limits while optionally cleaning and trimming certain attributes. The function is particularly useful when working with language models that impose token limits or when preserving the full HTML structure is crucial.

**Parameters:**

- `html`: A string containing the HTML code to be chunked.
- `max_tokens`: The maximum token length allowed for each chunk.
- `is_clean_html`: A boolean parameter specifying whether to clean the HTML before chunking. If set to `True`, the function applies a cleaning process that removes hidden elements, styles, scripts, and trims attributes to a specified length. By default, it is set to `True`, but you can disable this to retain the original HTML without cleaning.
- `attr_cutoff_len`: An integer that sets the cutoff length for attributes in the HTML tags, based on string length. This parameter is particularly useful for shortening overly long attributes (such as URLs) by retaining only the essential parts (e.g., domain names) without affecting the core meaning of the attribute. You can also disable this feature by setting it to `0` or not providing it.

The output should consists of several HTML chunks, where each chunk contains valid HTML code with preserved structure and attributes, and any excessively long attributes are truncated to the specified length. In this case we have

```
[
    '<html darker-dark-theme="" darker-dark-theme-deprecate="" lang="en" style="font-size: 10px;font-family: Roboto, Arial, sans-serif;" system-icons="" typography="" typography-spacing=""><body><ytd-app><ytd-masthead class="shell" id="masthead" logo-type="YOUTUBE_LOGO" slot="masthead"><div class="ytd-searchbox-spt" id="search-container" slot="search-container"></div><div class="ytd-searchbox-spt" id="search-input" slot="search-input"><input autocapitalize="none" autocomplete="off" autocorrect="off" hidden="" id="search" name="search_query" spellcheck="false" tabindex="0" type="text"/></div></ytd-masthead></ytd-app></body></html>', 

    '<html darker-dark-theme="" darker-dark-theme-deprecate="" lang="en" style="font-size: 10px;font-family: Roboto, Arial, sans-serif;" system-icons="" typography="" typography-spacing=""><body><ytd-app><ytd-masthead class="shell" id="masthead" logo-type="YOUTUBE_LOGO" slot="masthead"><svg class="external-icon" id="menu-icon" preserveaspectratio="xMidYMid meet"><g class="yt-icons-ext" id="menu" viewbox="0 0 24 24"><path d="M21,6H3V5h18V6z M21,11H3v"></path></g></svg><div id="masthead-logo" slot="masthead-logo"><span id="country-code"></span></div></ytd-masthead></ytd-app></body></html>', 
    
    '<html darker-dark-theme="" darker-dark-theme-deprecate="" lang="en" style="font-size: 10px;font-family: Roboto, Arial, sans-serif;" system-icons="" typography="" typography-spacing=""><body><ytd-app><ytd-masthead class="shell" id="masthead" logo-type="YOUTUBE_LOGO" slot="masthead"><div id="masthead-skeleton-icons" slot="masthead-skeleton"><div class="masthead-skeleton-icon"></div><div class="masthead-skeleton-icon"></div><div class="masthead-skeleton-icon"></div></div></ytd-masthead></ytd-app><link href="https://www.youtube.com/s" name="www-main-desktop-watch-page-skeleton" nonce="2kzKHraEELEaWexSX3PyNg" rel="stylesheet"/></body></html>'
]
```

#### Comparison with Existing Methods

**LangChain (HTMLHeaderTextSplitter & HTMLSectionSplitter) and LlamaIndex (HTMLNodeParser)**:
   - **Limitations**: These methods split text at the element level and add metadata for each header relevant to the chunk. However, they extract only the text content and exclude the HTML structure, attributes, and other non-text elements, limiting their use for tasks requiring the full HTML context.
   - **Advantage of this Method**: Our algorithm preserves the full HTML structure, including the DOM path, tags, and attributes. This makes it far more suitable for tasks like web understanding, where the entire HTML syntax is essential for accurate processing.

**google-labs-html-chunker**:
   - **Limitations**: This method also uses BeautifulSoup to parse HTML into a DOM tree, and aggregates text content from leaf nodes and attempts to merge them until a word limit is reached. While it employs a greedy merging approach similar to ours, the output is restricted to text, not the complete HTML.
   - **Advantage of this Method**: In contrast, our greedy merging algorithm combines HTML chunks while retaining the entire HTML syntax. This allows our method to generate full HTML chunks, making it far more versatile for use cases that require HTML as input, not just the text content.


#### Contact Us

If you are interested in collaborating with us on this project or have any questions, please feel free to reach out to us. We are open to discussing potential applications, data sharing, and other opportunities for collaboration.

Find Jiarun Liu on his [Github](https://github.com/KLGR123).