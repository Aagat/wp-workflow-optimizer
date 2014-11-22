FROM wordpress:latest

COPY docker-entrypoint.sh /entrypoint.sh

RUN ["chmod","a+x","/entrypoint.sh"]

ENTRYPOINT ["/entrypoint.sh"]

EXPOSE 80

CMD ["apache2", "-DFOREGROUND"]
