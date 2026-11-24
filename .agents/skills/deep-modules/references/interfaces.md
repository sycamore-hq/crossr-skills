# Interfaces

A type guards its data. A module shows less than it hides.

## Rules

MD-03  No field leaks. When a type keeps any field to itself and has its own methods over its fields, code outside the type and its tangle does not write, mutably borrow, index, or call mutating methods on those fields, directly or through getters and setters. Copying a value out, or a read-only query such as `len` or `is_empty`, is not a leak.

MD-04  No shallow modules. A crate, package, or module with child modules that shows outside callers more than seven functions must hide more functions than it shows, and no list a reader must learn (its exported types, or one type's functions) runs longer than seven.

## How

A field leak is a decision made in the wrong place. If three callers each do `queue.items.push(x); queue.head += 1`, the queue's invariant now lives in three files. Look at the pattern across all the call sites before fixing any of them, then give the type the operation those callers were assembling: `queue.push(x)`, `queue.pop()`, `queue.backlog()`. Fix leaks as a group, never one call site at a time. Turning `pub items` into `fn items_mut()` changes the spelling, not the leak.

What is not a leak: copying a number or a flag out of a field, borrowing plain data to read it, a read-only query on it (`len`, `is_empty`, `contains`), or a method that forwards one call to a field so callers never see it. Iterating a field's internals to recompute something the type could answer is a smell to raise in review, not an automatic leak. Visibility keywords do not decide it; usage does.

A shallow module is one whose interface costs as much to learn as its body. Count the functions outsiders actually call, not what is marked public. If `app` calls nine of `store`'s fifteen functions, find the three or so things `app` is really trying to do (`open`, `load`, `summary`) and make those the interface; the other functions go private behind them.

Several small types pass where one wide type fails: a reader learns an interface one list at a time, so four types with four methods each is easier than one type with sixteen.

Trait implementations and thin wrappers do not count toward what a module shows; they are part of using a type, not learning it.
