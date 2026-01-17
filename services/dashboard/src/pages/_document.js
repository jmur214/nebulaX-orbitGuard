import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
    return (
        <Html lang="en">
            <Head>
                <link rel="stylesheet" href="/cesium/Widgets/widgets.css" />
                <script
                    dangerouslySetInnerHTML={{
                        __html: `
              window.CESIUM_BASE_URL = '/cesium';
            `,
                    }}
                />
            </Head>
            <body>
                <Main />
                <NextScript />
            </body>
        </Html>
    );
}
