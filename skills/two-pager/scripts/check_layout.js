() => {
  const issues = [];
  const context = document.createElement('canvas').getContext('2d');
  const pages = Array.from(document.querySelectorAll('article.page'));
  if (pages.length !== 2) issues.push({type:'page-count', expected:2, actual:pages.length});
  pages.forEach((page, index) => {
    const pageNumber = index + 1;
    const bounds = page.getBoundingClientRect();
    const content = page.querySelector('.content');
    const limit = content?.getBoundingClientRect().bottom ?? bounds.bottom;
    const boxes = [];
    const record = (issue) => issues.push({page:pageNumber, ...issue});
    for (const column of page.querySelectorAll('.content > .column')) {
      if (column.lastElementChild?.getBoundingClientRect().bottom > limit + 1)
        record({type:'column-overflow', text:column.querySelector('h2')?.textContent});
    }
    const walker = document.createTreeWalker(page, NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) {
      const node = walker.currentNode;
      const parent = node.parentElement;
      if (!node.textContent.trim() || parent.closest('script,style,[data-qa-ignore]')) continue;
      const range = document.createRange();
      range.selectNodeContents(node);
      const style = getComputedStyle(parent);
      context.font = `${style.fontStyle} ${style.fontWeight} ${style.fontSize} ${style.fontFamily}`;
      const metrics = context.measureText(node.textContent.trim());
      for (const rect of range.getClientRects()) {
        if (!rect.width || !rect.height) continue;
        const text = node.textContent.trim().slice(0,160);
        const box = {left:rect.left,top:rect.top,right:rect.right,bottom:rect.bottom,text};
        // CJK font boxes include leading; compare ink bounds when the untransformed font metrics match.
        if (Math.abs(rect.height - metrics.fontBoundingBoxAscent - metrics.fontBoundingBoxDescent) <= 2) {
          const baseline = rect.bottom - metrics.fontBoundingBoxDescent;
          box.top = baseline - metrics.actualBoundingBoxAscent - 1;
          box.bottom = baseline + metrics.actualBoundingBoxDescent + 1;
        }
        if (box.left < bounds.left-1 || box.right > bounds.right+1 || box.top < bounds.top-1 || box.bottom > bounds.bottom+1)
          record({type:'outside-page',text});
        if (parent.closest('.content') && box.bottom > limit+1)
          record({type:'below-content',text});
        const owner = parent.closest('td,th,.column');
        if (owner) {
          const ownBounds = owner.getBoundingClientRect();
          if (rect.left < ownBounds.left-1 || rect.right > ownBounds.right+1)
            record({type:'outside-column',text});
        }
        boxes.push(box);
      }
    }
    for (const img of page.querySelectorAll('img:not([data-qa-ignore])')) {
      if (img.closest('[data-qa-ignore]')) continue;
      const rect = img.getBoundingClientRect();
      if (!img.complete || img.naturalWidth === 0) record({type:'broken-image',text:img.alt});
      if (rect.left < bounds.left-1 || rect.right > bounds.right+1 || rect.bottom > bounds.bottom+1)
        record({type:'outside-page',text:img.alt});
      if (img.closest('.content') && rect.bottom > limit+1)
        record({type:'below-content',text:img.alt});
      boxes.push({left:rect.left,top:rect.top,right:rect.right,bottom:rect.bottom,text:`Image: ${img.alt}`});
    }
    // shortcut: O(n²) rectangle comparison, use a spatial index if briefs grow past two pages.
    for (let i=0; i<boxes.length; i++) for (let j=i+1; j<boxes.length; j++) {
      const a=boxes[i], b=boxes[j];
      if (Math.min(a.right,b.right)-Math.max(a.left,b.left)>1 && Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1)
        record({type:'overlap',a:a.text,b:b.text});
    }
  });
  return {pageCount:pages.length, sizes:pages.map(p => ({width:p.offsetWidth,height:p.offsetHeight})), issues};
}
