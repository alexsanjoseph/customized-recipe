max_width, padding_top, padding_right, padding_left, padding_bottom = 1200, 5, 5, 5, 5
current_css = f"""
<style>
    .reportview-container .main .block-container{{
        max-width: {max_width}px;
        padding-top: {padding_top}rem;
        padding-right: {padding_right}rem;
        padding-left: {padding_left}rem;
        padding-bottom: {padding_bottom}rem;
    }}
</style>
"""
