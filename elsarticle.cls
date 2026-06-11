%%
%% Minimal elsarticle.cls for local compilation
%% Full version: https://ctan.org/pkg/elsarticle
%%
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{elsarticle}[2024/01/01 Elsevier article class (minimal)]

\DeclareOption{review}{\relax}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax

\LoadClass[12pt,a4paper]{article}

\RequirePackage[margin=1in]{geometry}
\RequirePackage{graphicx}
\RequirePackage{booktabs}
\RequirePackage{multirow}
\RequirePackage{hyperref}
\RequirePackage{setspace}

% Frontmatter
\newenvironment{frontmatter}{%
  \clearpage\thispagestyle{plain}%
}{%
  \bigskip
}

% Title
\renewcommand{\title}[2][]{%
  \gdef\@title{#2}\gdef\@shorttitle{#1}%
}
\renewcommand{\maketitle}{%
  \begin{center}
    {\LARGE\bfseries\@title\par}
    \vskip 1em
    {\large\@author\par}
    \vskip 1em
  \end{center}
}

% Abstract
\renewenvironment{abstract}{%
  \small\begin{center}{\bfseries Abstract}\end{center}\quotation
}{%
  \endquotation
}

% Keywords
\newenvironment{keyword}{%
  \small\noindent{\bfseries Keywords: }%
}{\par}

% Journal
\newcommand{\journal}[1]{\gdef\@journal{#1}}

% Page style
\pagestyle{plain}
