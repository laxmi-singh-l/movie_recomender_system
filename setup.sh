mkdir -p ~/.streamlit/

echo "\
[server]\n\
port = $PORT\n\
enableCORE = false\n\
headless = true\n\
\n\
" > ~/.streamlit/config.tomal
